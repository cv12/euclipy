import networkx as nx
import matplotlib.pyplot as plt
import sys

sys.path.append('../')

from euclipy.polygon import Triangle
from euclipy.core import DIRECTED_GRAPH

Triangle("A B C").triangle_sum_theorem()
Triangle('A B C').angles[0].measure = 30
Triangle('A B C').angles[1].measure = 60
Triangle('A B C').solver.solve()
Triangle("A B C").pythagorean_theorem()
Triangle('D E F').angles[0].measure = 45
G = DIRECTED_GRAPH
color_order = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan']
pos = nx.shell_layout(G)
nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_color = 'red', node_size = 500)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, edge_color='r', arrows=True)
nx.draw_networkx_edges(G, pos, arrows=False)
plt.tight_layout()
plt.show()

