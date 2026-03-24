import os
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, RegularPolygon, Polygon

from MarkovDecision import compare_strategies


trapLayouts = {
    "no_trap_layout": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    "few_traps_layout": [0,0,2,0,0,0,2,0,0,0,0,2,0,0,0],
    "many_traps_layout": [0, 0, 1, 1, 3, 2, 1, 3, 2, 1, 1, 0, 1, 1, 0],
    "two_in_a_row_layout": [0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 2, 0],
    "evil_fast_lane_layout": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 1, 0],
    "back_to_3_layout": [0,0,0,0,0,2,0,0,0,1,0,0,2,0,0],
}


# draws one game board with node shapes and dice-policy colors
def drawSingleBoard(axis, trapLayout, dicePolicy=None, stateValues=None):
    tileShapeMap = {0: 's', 1: 'o', 2: '<', 3: '8'}

    diceColorMap = {
        1: '#2ca02c',
        2: '#f1c40f',
        3: '#ff7f0e',
        4: '#d62728',
    }

    def getTileColor(tileIndex):
        if dicePolicy is None or tileIndex == 15:
            return 'black'
        return diceColorMap.get(int(dicePolicy[tileIndex - 1]), 'black')

    graph = nx.DiGraph()

    for i in range(1, 10):
        graph.add_edge(str(i), str(i + 1))
    graph.add_edge("10", "15")

    graph.add_edges_from([
        ("3", "11"),
        ("11", "12"),
        ("12", "13"),
        ("13", "14"),
        ("14", "15"),
    ])

    nodePositions = {}
    mainPathNodes = [str(x) for x in range(1, 11)] + ["15"]

    startX = 0.7
    deltaX = 0.6
    for i, node in enumerate(mainPathNodes):
        nodePositions[node] = (startX + i * deltaX, 0.0)

    nodePositions["11"] = (nodePositions["4"][0], -0.2)
    nodePositions["12"] = (nodePositions["6"][0], -0.2)
    nodePositions["13"] = (nodePositions["8"][0], -0.2)
    nodePositions["14"] = (nodePositions["10"][0], -0.2)

    nodeSize = 1650

    for trapType, nodeShape in tileShapeMap.items():
        matchingNodes = [str(i + 1) for i, t in enumerate(trapLayout) if t == trapType]
        if not matchingNodes:
            continue

        nodeColors = [getTileColor(int(n)) for n in matchingNodes]

        nx.draw_networkx_nodes(
            graph,
            nodePositions,
            nodelist=matchingNodes,
            node_shape=nodeShape,
            node_size=nodeSize,
            node_color=nodeColors,
            edgecolors='black',
            linewidths=1.2,
            ax=axis
        )

    if stateValues is None:
        labels = {n: n for n in nodePositions}
    else:
        fullValues = list(stateValues) + [0.0]
        labels = {}
        for n in nodePositions:
            tileIndex = int(n) - 1
            labels[n] = f"{fullValues[tileIndex]:.1f}"

    nx.draw_networkx_labels(
        graph,
        nodePositions,
        labels=labels,
        font_size=15,
        font_color='white',
        font_weight='normal',
        ax=axis
    )

    straightEdges = [
        ("1", "2"), ("2", "3"), ("3", "4"), ("4", "5"),
        ("5", "6"), ("6", "7"), ("7", "8"), ("8", "9"),
        ("9", "10"), ("10", "15"),
        ("11", "12"), ("12", "13"), ("13", "14"),
    ]

    nx.draw_networkx_edges(
        graph,
        nodePositions,
        edgelist=straightEdges,
        arrows=True,
        arrowstyle='->',
        arrowsize=16,
        width=1.4,
        node_size=nodeSize,
        min_source_margin=8,
        min_target_margin=8,
        ax=axis
    )

    x3, y3 = nodePositions["3"]
    x11, y11 = nodePositions["11"]
    axis.add_patch(FancyArrowPatch(
        (x3 - 0.05, y3 - 0.01),
        (x11 - 0.09, y11 - 0.02),
        arrowstyle='->',
        mutation_scale=16,
        linewidth=1.4,
        shrinkA=10,
        shrinkB=10,
        connectionstyle="arc3,rad=0.0",
        color="black"
    ))

    x14, y14 = nodePositions["14"]
    x15, y15 = nodePositions["15"]
    axis.add_patch(FancyArrowPatch(
        (x14 + 0.01, y14 - 0.01),
        (x15 - 0.07, y15 - 0.04),
        arrowstyle='->',
        mutation_scale=16,
        linewidth=1.4,
        shrinkA=10,
        shrinkB=10,
        connectionstyle="arc3,rad=0.0",
        color="black"
    ))

    axis.set_xlim(0.1, nodePositions["15"][0] + 0.7)
    axis.set_ylim(-0.78, 0.14)
    axis.axis('off')


# draws the legend for tile types and dice decisions
def drawKey(axis):
    axis.axis('off')
    axis.set_xlim(0.05, 1.05)
    axis.set_ylim(-0.05, 0.95)
    axis.set_aspect('equal', adjustable='box')

    borderColor = "#163646"
    lineWidth = 1.3
    boxLineWidth = 1.4
    diceColors = ['#2ca02c', '#f1c40f', '#ff7f0e', '#d62728']

    boxX = 0.05
    boxY = 0.06
    boxWidth = 0.90
    boxHeight = 0.88

    axis.add_patch(Rectangle(
        (boxX, boxY),
        boxWidth,
        boxHeight,
        fill=False,
        edgecolor="black",
        linewidth=boxLineWidth
    ))

    dividerY = 0.78
    axis.plot(
        [boxX, boxX + boxWidth],
        [dividerY, dividerY],
        color="black",
        linewidth=1.0
    )

    axis.text(0.5, 0.855, "Key", ha="center", va="center", fontsize=22, fontweight="bold")
    axis.text(0.5, 0.69, "Tile Types", ha="center", va="center", fontsize=16, fontweight="bold")

    tileXs = [0.18, 0.40, 0.62, 0.84]
    labelY = 0.59
    shapeY = 0.5
    tileNames = ["Regular", "Penalty", "Prison", "Restart"]

    for x, name in zip(tileXs, tileNames):
        axis.text(x, labelY, name, ha="center", va="bottom", fontsize=13)

    shapeSize = 0.15

    axis.add_patch(Rectangle(
        (tileXs[0] - shapeSize / 2, shapeY - shapeSize / 2),
        shapeSize,
        shapeSize,
        fill=False,
        edgecolor=borderColor,
        linewidth=lineWidth
    ))

    triX = tileXs[1]
    triY = shapeY
    triW = shapeSize * 1.08
    triH = shapeSize * 1.08

    axis.add_patch(Polygon([
        (triX - triW / 2, triY),
        (triX + triW / 2, triY + triH / 2),
        (triX + triW / 2, triY - triH / 2),
    ], closed=True, fill=False, edgecolor=borderColor, linewidth=lineWidth, joinstyle='miter'))

    axis.add_patch(RegularPolygon(
        (tileXs[2], shapeY),
        numVertices=8,
        radius=shapeSize / 2,
        orientation=np.pi / 8,
        fill=False,
        edgecolor=borderColor,
        linewidth=lineWidth
    ))

    axis.add_patch(Circle(
        (tileXs[3], shapeY),
        radius=shapeSize / 2,
        fill=False,
        edgecolor=borderColor,
        linewidth=lineWidth
    ))

    axis.plot([0.12, 0.88], [0.34, 0.34], color="#c9c9c9", linewidth=1.0)

    axis.text(0.5, 0.27, "Dice Decision", ha="center", va="center", fontsize=16, fontweight="bold")

    barY = 0.08
    barHeight = 0.10
    totalBarWidth = 0.85
    barWidth = totalBarWidth / 4.0
    startX = 0.5 - totalBarWidth / 2

    for i, color in enumerate(diceColors, start=1):
        x = startX + (i - 1) * barWidth

        axis.text(x + barWidth / 2, 0.18, str(i), ha="center", va="bottom", fontsize=13)

        axis.add_patch(Rectangle(
            (x, barY),
            barWidth,
            barHeight,
            facecolor=color,
            edgecolor=borderColor,
            linewidth=1.2
        ))


# draws the full figure with two boards and the shared key
def drawLayoutFigure(
    layoutName,
    trapLayout,
    policyCircleTrue,
    policyCircleFalse,
    valuesCircleTrue,
    valuesCircleFalse,
    savePath
):
    figure = plt.figure(figsize=(16.2, 6.9))

    gridSpec = figure.add_gridspec(
        2, 2,
        width_ratios=[6.2, 1.95],
        height_ratios=[1, 1],
        wspace=0.01,
        hspace=0.02
    )

    axisTop = figure.add_subplot(gridSpec[0, 0])
    axisBottom = figure.add_subplot(gridSpec[1, 0])
    axisKey = figure.add_subplot(gridSpec[:, 1])

    figure.suptitle(layoutName, fontsize=35, fontweight="bold", y=0.955)

    drawSingleBoard(axisTop, trapLayout, policyCircleTrue, valuesCircleTrue)
    drawSingleBoard(axisBottom, trapLayout, policyCircleFalse, valuesCircleFalse)
    drawKey(axisKey)

    axisTop.set_title("circle = True", fontsize=20, pad=1)
    axisBottom.set_title("circle = False", fontsize=20, pad=1)

    plt.subplots_adjust(left=0.035, right=0.985, top=0.88, bottom=0.06)

    posTop = axisTop.get_position()
    axisTop.set_position([posTop.x0, posTop.y0 - 0.1, posTop.width, posTop.height])

    plt.savefig(savePath, bbox_inches="tight")
    plt.close(figure)


# runs all layouts and saves the generated board figures
def runAll(outputDirectory="mdp_outputs"):
    os.makedirs(outputDirectory, exist_ok=True)

    for layoutName, trapLayout in trapLayouts.items():
        print("Running", layoutName)

        resultsTrue = compare_strategies(trapLayout, True)
        resultsFalse = compare_strategies(trapLayout, False)

        drawLayoutFigure(
            layoutName,
            trapLayout,
            resultsTrue["Optimal_policy"],
            resultsFalse["Optimal_policy"],
            resultsTrue["Optimal_cost"],
            resultsFalse["Optimal_cost"],
            os.path.join(outputDirectory, f"{layoutName}.pdf")
        )


# runs the script when called directly
if __name__ == "__main__":
    runAll()