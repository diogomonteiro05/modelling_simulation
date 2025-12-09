import xml.etree.ElementTree as ET
import random

# Paths
VCI_NET = "vci.net.xml"
OUTPUT_TRIPS = "trips_vci_generated.xml"

print("Extracting edges from vci.net.xml...")
tree = ET.parse(VCI_NET)
root = tree.getroot()

# Get all valid edges (exclude internal junction edges)
edges = []
for edge in root.findall(".//edge"):
    edge_id = edge.get("id")
    if edge_id and not edge_id.startswith(":"):
        edges.append(edge_id)

print(f"Found {len(edges)} edges")

# Use a smaller subset of most common/main edges that are more likely to be connected
# These are edges that appear frequently in the network as major routes
main_edges = ['1135405', '1302641', '1051139', '1181568', '1181543', '1398689']

# Generate trips using main edges (higher connectivity)
print("\nGenerating trips with high-connectivity edges...")
num_vehicles = 5000  # Generate more trips to compensate for invalids
begin_time = 32400   # 9:00 AM
end_time = 39600     # 11:00 AM  
duration = end_time - begin_time

trips_root = ET.Element("routes")
trips_root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
trips_root.set("xsi:noNamespaceSchemaLocation", "http://sumo.dlr.de/xsd/routes_file.xsd")

# Create trips
for i in range(num_vehicles):
    trip = ET.SubElement(trips_root, "trip")
    trip.set("id", str(i))
    depart_time = begin_time + (i / num_vehicles) * duration  # Spread evenly
    trip.set("depart", f"{depart_time:.2f}")
    
    # 70% use main edges (better connectivity), 30% random
    if random.random() < 0.7:
        trip.set("from", random.choice(main_edges))
        trip.set("to", random.choice(main_edges))
    else:
        trip.set("from", random.choice(edges))
        trip.set("to", random.choice(edges))

# Write trips
trips_tree = ET.ElementTree(trips_root)
ET.indent(trips_tree, space="    ")
trips_tree.write(OUTPUT_TRIPS, encoding="utf-8", xml_declaration=True)
print(f"Created {num_vehicles} trips in {OUTPUT_TRIPS}")
