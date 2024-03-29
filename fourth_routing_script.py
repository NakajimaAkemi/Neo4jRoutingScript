from routingpy import Graphhopper,OSRM, Valhalla
from neo4j import GraphDatabase
import time

# Connessione al database Neo4j
uri = "bolt://localhost:7687"
user="neo4j"
password="tesinatesina"


# Define the clients and their profile parameter
apis = (
   (Graphhopper(api_key='YOUR-API-KEY'), 'foot'),
   (Valhalla(),'pedestrian'),
   (OSRM(),'foot'),
)

def extract_AtoB(tx):
    query = """
        MATCH (n1:FootJunction), (n2:FootJunction)
        WHERE n1 <> n2 and n2.id<>"5567795278" and n2.id<>"5567795284"
        WITH n1, n2, rand() AS r
        ORDER BY r
        LIMIT 1
        RETURN n1.lat as lat,  n1.lon as lon, n2.lat as lat2,  n2.lon as lon2,n1.id as id1 ,n2.id as id2
        """
    data = []
    for record in tx.run(query):
        #print([[record["lon"], record["lat"]],[record["lon2"], record["lat2"]]])
        data.append([[record["lon"], record["lat"]],[record["lon2"], record["lat2"]]])
        #data.append([record["lon"], record["lat"],[record["lon2"], record["lat2"]]])
        print("###################################################################################")
        print("node ids:"+str(record["id1"]) +"----->"+record["id2"])
        print("###################################################################################")

    return data


if __name__ == "__main__":
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
            coordinates=session.execute_read(extract_AtoB)
            for coords in coordinates:
                print(coords)
                for api in apis:
                    client, profile = api
                    start_time = time.time()
                    route = client.directions(locations=coords, profile=profile)
                    print("###########################################################################")
                    print("Direction - {}\n\tDistance: {}".format(client.__class__.__name__,
                                                                            route.distance))
                    print("number of steps:")
                    print(len(route.geometry))
                    #print("#Geometry#")
                    #print(route.geometry)
                    print("###########################################################################")
                    print("--- %s seconds ---" % (time.time() - start_time))
