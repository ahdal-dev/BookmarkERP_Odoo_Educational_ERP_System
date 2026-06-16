from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://ba804be3.databases.neo4j.io"  
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ZlLUvIpEgybcMO53fjds_ubVj6nTSYrIbiajBSCouNY"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Test function
def test_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()
            print("Connection successful! Test query result:", record["test"])
    except Exception as e:
        print("Connection failed:", e)
    finally:
        driver.close()

# Run the test
test_connection()