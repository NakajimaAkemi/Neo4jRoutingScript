from routingpy import Graphhopper,OSRM, Valhalla
from neo4j import GraphDatabase

# Connessione al database Neo4j
uri = "bolt://localhost:7687"
user="neo4j"
password="tesinatesina"


# Define the clients and their profile parameter
apis = (
   (Graphhopper(api_key='77ae00f6-ff40-40c3-a039-e1b2bfaef4c8'), 'foot'),
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
    for record in tx.run(query):
         data.append(record["distance"])
    return data

if __name__ == "__main__":
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        coords=session.execute_read(extract_AtoB)
#        print(coords)
        for api in apis:
            client, profile = api
            route = client.directions(locations=coords, profile=profile)
            print("###########################################################################")
            print("Direction - {}:\n\tDuration: {}\n\tDistance: {}".format(client.__class__.__name__,
                                                                        route.duration,
                                                                        route.distance))
            print("#Geometry#")
            print(route.geometry)
            print("###########################################################################")

        print("###############################################################################")
        print("Distances in Neo4j:" + str(session.execute_read(extract_AtoB_step_mode_distances)))
        print("##############################################################################")