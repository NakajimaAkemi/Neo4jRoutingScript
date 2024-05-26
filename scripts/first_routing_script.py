from routingpy import Graphhopper,OSRM, Valhalla
from neo4j import GraphDatabase

# Connessione al database Neo4j
uri = "bolt://localhost:7687"
user="neo4j"
password="password"


# Define the clients and their profile parameter
apis = (
   (Graphhopper(api_key='YOUR-API-KEY'), 'foot'),
   (Valhalla(),'pedestrian'),
   (OSRM(),'foot'),
)

def extract(tx):
    query = """
        MATCH (a:FootJunction)
        WHERE a.id="315614392" OR a.id="1945691565"
        RETURN a.lat AS lat, a.lon AS lon
        """
    data = []
    for record in tx.run(query):
        data.append([record["lon"], record["lat"]])
    return data


if __name__ == "__main__":
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        coords=session.execute_read(extract)
        for api in apis:
            client, profile = api
            route = client.directions(locations=coords, profile=profile)
            print("Direction - {}:\n\tDuration: {}\n\tDistance: {}".format(client.__class__.__name__,
                                                                        route.duration,
                                                                        route.distance))
            #isochrones = client.isochrones(locations=coords[0], profile=profile, intervals=[600, 1200])
            #for iso in isochrones:
            #    print("Isochrone {} secs - {}:\n\tArea: {} sqm".format(client.__class__.__name__,
            #                                                           iso.interval,
            #                                                           Polygon(iso.geometry).area))
            #matrix = client.matrix(locations=coords, profile=profile)
            #print("Matrix - {}:\n\tDurations: {}\n\tDistances: {}".format(client.__class__.__name__,
            #                                                            matrix.durations,
            #                                                            matrix.distances))
