"""
============================================================================
FastAPI API Gateway for Educational ERP System
============================================================================
Purpose: Internal API Gateway and orchestration layer for microservices
Architecture: Receives requests from NGINX and routes to AI/Odoo services
Author: Educational ERP Development Team
Version: 1.0.0
============================================================================
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from functools import wraps

from fastapi import (
    FastAPI, 
    HTTPException, 
    Depends, 
    UploadFile, 
    File, 
    Header,
    status,
    Request,
    BackgroundTasks,
    Form
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr, validator
import httpx
import jwt
from jwt.exceptions import InvalidTokenError
import asyncio
from enum import Enum

# ============================================================================
# Configuration and Environment Variables
# ============================================================================

# Environment Configuration
OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://ocr_microservice:5000")
ODOO_URL = os.getenv("ODOO_URL", "http://odoo:8069")
ODOO_DB = os.getenv("ODOO_DB", "edu_demo_new")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI Application Initialization
# ============================================================================

app = FastAPI(
    title="Educational ERP API Gateway",
    description="Central API Gateway for Educational ERP Microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json"
)

# ============================================================================
# CORS Middleware Configuration
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models - Request/Response Schemas
# ============================================================================

class UserRole(str, Enum):
    """
    User roles for Role-Based Access Control (RBAC)
    """
    PROSPECTIVE_STUDENT = "prospective_student"
    ADMISSION_STAFF = "admission_staff"
    ADMIN = "admin"
    SYSTEM = "system"


class TokenData(BaseModel):
    """JWT Token payload structure"""
    user_id: int
    username: str
    email: EmailStr
    role: UserRole
    exp: datetime


class OCRResponse(BaseModel):
    """Response from OCR Microservice"""
    success: bool
    extracted_data: Dict[str, Any]
    confidence: Optional[float] = None
    processing_time: Optional[float] = None


class AdmissionApplicationData(BaseModel):
    """
    Structured data for admission application
    Extracted from OCR or manually entered
    """
    # Personal Information
    full_name: str = Field(..., min_length=2, max_length=200)
    national_id: str = Field(..., pattern=r'^\d{14}$')  # Egyptian NID format
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    date_of_birth: datetime
    
    # Address Information
    address: str = Field(..., min_length=10)
    city: str
    country: str = "Egypt"
    
    # Academic Information
    previous_qualification: str
    graduation_year: int = Field(..., ge=1950, le=2030)
    gpa: float = Field(..., ge=0.0, le=4.0)
    
    # Application Details
    desired_program: str
    application_type: str = "regular"
    
    @validator('graduation_year')
    def validate_graduation_year(cls, v):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError('Graduation year cannot be in the future')
        return v


class AdmissionResponse(BaseModel):
    """Response from Odoo Admission Module"""
    success: bool
    application_id: Optional[int] = None
    student_id: Optional[int] = None
    status: str
    message: str
    next_steps: Optional[List[str]] = None


class OrchestrationRequest(BaseModel):
    """Request for orchestrated document processing + admission"""
    email: EmailStr
    phone: str
    desired_program: str
    application_type: str = "regular"


class OrchestrationResponse(BaseModel):
    """Response from orchestrated workflow"""
    success: bool
    ocr_result: Optional[OCRResponse] = None
    admission_result: Optional[AdmissionResponse] = None
    execution_time: float
    errors: Optional[List[str]] = None


# ============================================================================
# Security - JWT Authentication and RBAC
# ============================================================================

security = HTTPBearer()


class RBACChecker:
    """
    Role-Based Access Control (RBAC) Checker
    Validates JWT tokens and enforces role-based permissions
    """
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> TokenData:
        """
        Validate JWT token and check user permissions
        
        Args:
            credentials: Bearer token from Authorization header
            
        Returns:
            TokenData: Validated user data
            
        Raises:
            HTTPException: If token is invalid or user lacks permission
        """
        token = credentials.credentials
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY, 
                algorithms=[JWT_ALGORITHM]
            )
            
            # Extract user data
            token_data = TokenData(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                email=payload.get("email"),
                role=UserRole(payload.get("role")),
                exp=datetime.fromtimestamp(payload.get("exp"))
            )
            
            # Check if token is expired
            if token_data.exp < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Check role-based permissions
            if token_data.role not in self.allowed_roles:
                logger.warning(
                    f"Access denied for user {token_data.username} "
                    f"with role {token_data.role}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: "
                           f"{[role.value for role in self.allowed_roles]}",
                )
            
            logger.info(
                f"Authenticated user: {token_data.username} "
                f"(Role: {token_data.role.value})"
            )
            
            return token_data
            
        except InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )


# ============================================================================
# Helper Functions - Odoo XML-RPC Client
# ============================================================================

class OdooClient:
    """
    Asynchronous Odoo XML-RPC Client
    Handles authentication and API calls to Odoo ERP
    """
    
    def __init__(self):
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USERNAME
        self.password = ODOO_PASSWORD
        self.uid: Optional[int] = None
    
    async def authenticate(self) -> int:
        """
        Authenticate with Odoo and get user ID
        
        Returns:
            int: User ID if authentication successful
        """
        if self.uid:
            return self.uid
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Odoo authentication endpoint
                auth_url = f"{self.url}/web/session/authenticate"
                
                payload = {
                    "jsonrpc": "2.0",
                    "params": {
                        "db": self.db,
                        "login": self.username,
                        "password": self.password
                    }
                }
                
                response = await client.post(auth_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if "result" in result and "uid" in result["result"]:
                    self.uid = result["result"]["uid"]
                    logger.info(f"Authenticated with Odoo as user ID: {self.uid}")
                    return self.uid
                else:
                    raise Exception("Authentication failed: No UID returned")
                    
        except Exception as e:
            logger.error(f"Odoo authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to Odoo ERP system"
            )
    
    async def create_admission_application(
        self, 
        application_data: AdmissionApplicationData
    ) -> Dict[str, Any]:
        """
        Create admission application in Odoo
        
        Args:
            application_data: Structured admission data
            
        Returns:
            dict: Created application details
        """
        await self.authenticate()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Odoo JSON-RPC endpoint for model operations
                url = f"{self.url}/web/dataset/call_kw"
                
                # Prepare application data for Odoo
                values = {
                    "name": application_data.full_name,
                    "national_id": application_data.national_id,
                    "email": application_data.email,
                    "phone": application_data.phone,
                    "date_of_birth": application_data.date_of_birth.strftime("%Y-%m-%d"),
                    "street": application_data.address,
                    "city": application_data.city,
                    "country_id": self._get_country_id(application_data.country),
                    "previous_qualification": application_data.previous_qualification,
                    "graduation_year": application_data.graduation_year,
                    "gpa": application_data.gpa,
                    "desired_program": application_data.desired_program,
                    "application_type": application_data.application_type,
                    "state": "draft",
                }
                
                payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "model": "op.admission",  # OpenEduCat admission model
                        "method": "create",
                        "args": [values],
                        "kwargs": {}
                    },
                    "id": 1
                }
                
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if "result" in result:
                    application_id = result["result"]
                    logger.info(f"Created admission application: {application_id}")
                    
                    return {
                        "application_id": application_id,
                        "status": "draft",
                        "message": "Application submitted successfully"
                    }
                else:
                    raise Exception("Failed to create application")
                    
        except Exception as e:
            logger.error(f"Failed to create admission application: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create admission application: {str(e)}"
            )
    
    def _get_country_id(self, country_name: str) -> int:
        """Get Odoo country ID (simplified - would query Odoo in production)"""
        # In production, this would query res.country model
        return 65  # Egypt's typical ID in Odoo


# Global Odoo client instance
odoo_client = OdooClient()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "api_gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """
    Basic metrics endpoint (extend with Prometheus in production)
    """
    return {
        "service": "api_gateway",
        "uptime": "operational",
        "endpoints_available": 5
    }


@app.post(
    "/api/v1/extract-document",
    response_model=OCRResponse,
    summary="Extract data from uploaded document using OCR",
    description="""
    Accepts an uploaded document (National ID, certificate, etc.) and 
    extracts structured data using the OCR Microservice.
    
    **Access:** Prospective students and admission staff
    **Rate Limit:** 2 requests/second (configured in NGINX)
    """
)
async def extract_document(
    file: UploadFile = File(..., description="Document image/PDF file"),
    user: TokenData = Depends(
        RBACChecker([
            UserRole.PROSPECTIVE_STUDENT, 
            UserRole.ADMISSION_STAFF,
            UserRole.ADMIN
        ])
    )
):
    """
    Route 1: OCR Service Integration
    
    Forwards uploaded document to OCR Microservice for text extraction
    """
    start_time = datetime.utcnow()
    
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {allowed_types}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )
        
        logger.info(
            f"Processing document: {file.filename} "
            f"({len(file_content)} bytes) for user {user.username}"
        )
        
        # Forward to OCR Microservice
        async with httpx.AsyncClient(timeout=90.0) as client:
            files = {"file": (file.filename, file_content, file.content_type)}
            
            response = await client.post(
                f"{OCR_SERVICE_URL}/ocr",
                files=files
            )
            
            response.raise_for_status()
            ocr_result = response.json()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(
            f"OCR processing completed in {processing_time:.2f}s "
            f"for user {user.username}"
        )
        
        return OCRResponse(
            success=True,
            extracted_data=ocr_result.get("result", {}),
            confidence=ocr_result.get("confidence", 0.0),
            processing_time=processing_time
        )
        
    except httpx.HTTPError as e:
        logger.error(f"OCR service communication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR service is currently unavailable"
        )
    except Exception as e:
        logger.error(f"Document extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document extraction failed: {str(e)}"
        )


@app.post(
    "/api/v1/admissions/apply",
    response_model=AdmissionResponse,
    summary="Submit admission application to Odoo",
    description="""
    Submits structured admission application data to Odoo ERP system.
    
    **Access:** Prospective students and admission staff
    **Rate Limit:** 5 requests/second with burst of 10
    """
)
async def submit_admission_application(
    application: AdmissionApplicationData,
    user: TokenData = Depends(
        RBACChecker([
            UserRole.PROSPECTIVE_STUDENT,
            UserRole.ADMISSION_STAFF,
            UserRole.ADMIN
        ])
    )
):
    """
    Route 2: Odoo Admission Module Integration
    
    Creates admission application in Odoo ERP system
    """
    try:
        logger.info(
            f"Creating admission application for {application.full_name} "
            f"(submitted by {user.username})"
        )
        
        # Create application in Odoo
        result = await odoo_client.create_admission_application(application)
        
        logger.info(
            f"Admission application created: ID {result['application_id']}"
        )
        
        return AdmissionResponse(
            success=True,
            application_id=result["application_id"],
            status=result["status"],
            message=result["message"],
            next_steps=[
                "Check your email for confirmation",
                "Wait for admission committee review",
                "Track application status in student portal"
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admission application submission failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit admission application: {str(e)}"
        )


@app.post(
    "/api/v1/admissions/submit-with-document",
    response_model=OrchestrationResponse,
    summary="Orchestrated workflow: OCR + Admission Application",
    description="""
    Composite endpoint that orchestrates the complete admission workflow:
    1. Extract data from uploaded document using OCR
    2. Validate and enrich extracted data
    3. Submit admission application to Odoo
    
    **Access:** Prospective students and admission staff
    **Rate Limit:** 2 requests/second (most restrictive)
    """
)
async def submit_with_document(
    file: UploadFile = File(..., description="National ID or certificate"),
    email: EmailStr = Form(..., description="Applicant email"),
    phone: str = Form(..., description="Applicant phone number"),
    desired_program: str = Form(..., description="Desired academic program"),
    application_type: str = Form("regular", description="Application type"),
    user: TokenData = Depends(
        RBACChecker([
            UserRole.PROSPECTIVE_STUDENT,
            UserRole.ADMISSION_STAFF,
            UserRole.ADMIN
        ])
    )
):
    """
    Route 3: Orchestration Endpoint
    
    Combines OCR extraction and admission application in single workflow
    """
    start_time = datetime.utcnow()
    errors = []
    ocr_result = None
    admission_result = None
    
    try:
        logger.info(
            f"Starting orchestrated admission workflow for user {user.username}"
        )
        
        # Step 1: Extract data from document using OCR
        try:
            file_content = await file.read()
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                files = {"file": (file.filename, file_content, file.content_type)}
                response = await client.post(
                    f"{OCR_SERVICE_URL}/ocr",
                    files=files
                )
                response.raise_for_status()
                ocr_data = response.json()
            
            ocr_result = OCRResponse(
                success=True,
                extracted_data=ocr_data.get("result", {}),
                confidence=ocr_data.get("confidence", 0.0)
            )
            
            logger.info("OCR extraction completed successfully")
            
        except Exception as e:
            error_msg = f"OCR extraction failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            raise
        
        # Step 2: Map OCR data to admission application structure
        try:
            extracted = ocr_result.extracted_data
            
            # Create application data from OCR results
            application_data = AdmissionApplicationData(
                full_name=extracted.get("name", "Unknown"),
                national_id=extracted.get("nid", "00000000000000"),
                email=email,
                phone=phone,
                date_of_birth=datetime.strptime(
                    extracted.get("date_of_birth", "2000-01-01"),
                    "%Y-%m-%d"
                ),
                address=extracted.get("address", "Not provided"),
                city=extracted.get("city", "Cairo"),
                country="Egypt",
                previous_qualification=extracted.get("qualification", "High School"),
                graduation_year=int(extracted.get("graduation_year", 2020)),
                gpa=float(extracted.get("gpa", 3.0)),
                desired_program=desired_program,
                application_type=application_type
            )
            
        except Exception as e:
            error_msg = f"Data mapping failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to map extracted data to application format"
            )
        
        # Step 3: Submit to Odoo
        try:
            odoo_result = await odoo_client.create_admission_application(
                application_data
            )
            
            admission_result = AdmissionResponse(
                success=True,
                application_id=odoo_result["application_id"],
                status=odoo_result["status"],
                message=odoo_result["message"],
                next_steps=[
                    "Document verified via OCR",
                    "Application submitted to admission office",
                    "Check email for updates"
                ]
            )
            
            logger.info(
                f"Orchestrated workflow completed: "
                f"Application ID {odoo_result['application_id']}"
            )
            
        except Exception as e:
            error_msg = f"Odoo submission failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            raise
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return OrchestrationResponse(
            success=True,
            ocr_result=ocr_result,
            admission_result=admission_result,
            execution_time=execution_time,
            errors=errors if errors else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Orchestrated workflow failed: {str(e)}")
        
        return OrchestrationResponse(
            success=False,
            ocr_result=ocr_result,
            admission_result=admission_result,
            execution_time=execution_time,
            errors=errors + [str(e)]
        )


# ============================================================================
# Utility Endpoints - JWT Token Generation (for testing)
# ============================================================================

@app.post("/api/v1/auth/token")
async def generate_test_token(
    username: str,
    role: UserRole = UserRole.PROSPECTIVE_STUDENT
):
    """
    Generate JWT token for testing purposes
    ** REMOVE IN PRODUCTION - Use proper authentication service **
    """
    payload = {
        "user_id": 1,
        "username": username,
        "email": f"{username}@example.com",
        "role": role.value,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600,
        "role": role.value
    }


# ============================================================================
# Application Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize connections and resources on startup"""
    logger.info("Starting FastAPI API Gateway...")
    logger.info(f"OCR Service URL: {OCR_SERVICE_URL}")
    logger.info(f"Odoo URL: {ODOO_URL}")
    
    # Test Odoo connection
    try:
        await odoo_client.authenticate()
        logger.info("Successfully connected to Odoo ERP")
    except Exception as e:
        logger.warning(f"Failed to connect to Odoo on startup: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Shutting down FastAPI API Gateway...")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
