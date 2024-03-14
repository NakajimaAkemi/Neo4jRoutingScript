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
        MATCH (a:FootNode)
        WHERE a.id="2021511952" OR a.id="1256958142"
        RETURN a.lat AS lat, a.lon AS lon
        """
    data = []
    for record in tx.run(query):
        #print(record)
        data.append([record["lon"], record["lat"]])
    return data

def extract_AtoB_step_mode_distances(tx):
    query = """
        MATCH (startNode:FootNode {id: "2021511952"})
        MATCH (endNode:FootNode {id: "1256958142"})
        CALL apoc.algo.dijkstra(startNode, endNode, "FOOT_ROUTE", "length") 
        YIELD weight, path
        UNWIND relationships(path) AS rel
        RETURN startNode.lat AS start_lat, startNode.lon AS start_lon,
               endNode.lat AS end_lat, endNode.lon AS end_lon,
               rel.distance AS distance
        """
    data = []
    total_distance=0
    for record in tx.run(query):
         data.append(record["distance"])
         total_distance+=float(record["distance"])
    return data,total_distance

if __name__ == "__main__":
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        coords=session.execute_read(extract_AtoB)
#        print(coords)
        for api in apis:
            client, profile = api
            start_time = time.time()
            route = client.directions(locations=coords, profile=profile)
            print("###########################################################################")
            print("Direction - {}\n\tDistance: {}".format(client.__class__.__name__,
                                                                        route.distance))
            print("#Geometry#")
            print(route.geometry)
            print("###########################################################################")
            print("--- %s seconds ---" % (time.time() - start_time))

        print("###############################################################################")
        steps,distance=session.execute_read(extract_AtoB_step_mode_distances)
        print("Distances in Neo4j:" + str(steps))
        print("Total distance weight: "+str(distance))
        print("##############################################################################")
