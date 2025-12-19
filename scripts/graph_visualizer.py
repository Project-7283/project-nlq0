from src.modules.graph_visualizer import GraphVisualizer
gv = GraphVisualizer.from_json("schemas/ecommerce_marketplace.json")
gv.draw(edge_label_attr="condition")  # or "weight"
