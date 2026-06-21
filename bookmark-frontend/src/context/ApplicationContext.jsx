import { createContext, useContext, useReducer } from 'react';

const initialState = {
  personalInfo: {
    name: '',
    email: '',
    phone: '',
    national_id: '',
    date_of_birth: '',
    nationality: 'Egyptian',
  },
  academicHistory: {
    previous_school: '',
    degree_program: '',
    gpa: '',
    graduation_year: '',
    application_type: 'regular',
  },
  ocrData: null,
  documentFile: null,
  documentFilename: null,
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_PERSONAL_INFO':
      return { ...state, personalInfo: { ...state.personalInfo, ...action.payload } };
    case 'SET_ACADEMIC_HISTORY':
      return { ...state, academicHistory: { ...state.academicHistory, ...action.payload } };
    case 'SET_OCR_DATA':
      return { ...state, ocrData: action.payload };
    case 'SET_DOCUMENT':
      return { ...state, documentFile: action.payload.file, documentFilename: action.payload.filename };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

const ApplicationContext = createContext(null);

export function ApplicationProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const setPersonalInfo = (data) => dispatch({ type: 'SET_PERSONAL_INFO', payload: data });
  const setAcademicHistory = (data) => dispatch({ type: 'SET_ACADEMIC_HISTORY', payload: data });
  const setOcrData = (data) => dispatch({ type: 'SET_OCR_DATA', payload: data });
  const setDocument = (file, filename) => dispatch({ type: 'SET_DOCUMENT', payload: { file, filename } });
  const reset = () => dispatch({ type: 'RESET' });

  return (
    <ApplicationContext.Provider value={{ state, setPersonalInfo, setAcademicHistory, setOcrData, setDocument, reset }}>
      {children}
    </ApplicationContext.Provider>
  );
}

export function useApplication() {
  const ctx = useContext(ApplicationContext);
  if (!ctx) throw new Error('useApplication must be used within ApplicationProvider');
  return ctx;
}
