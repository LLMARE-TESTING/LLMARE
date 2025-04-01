import json

# 读取数据文件
with open('/mnt/data/utg_add.js', 'r') as file:
    data = file.read()

# 去除多余的JavaScript语法
data = data.replace('var utg = ', '').rstrip(';')

# 解析JSON数据
utg = json.loads(data)

# HTML模板
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Graph Visualization</title>
    <style>
        .node image {
            width: 100px;
            height: 100px;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
        }
    </style>
    <script src="https://d3js.org/d3.v6.min.js"></script>
</head>
<body>
    <script>
        // 数据
        var utg = {data};

        // 创建SVG画布
        var width = 960, height = 600;
        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);

        // 定义力导向图
        var simulation = d3.forceSimulation(utg.nodes)
            .force("link", d3.forceLink(utg.edges).id(function(d) { return d.state_str; }).distance(200))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        // 定义边
        var link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(utg.edges)
            .enter().append("line")
            .attr("class", "link");

        // 定义节点
        var node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(utg.nodes)
            .enter().append("g");

        node.append("image")
            .attr("xlink:href", function(d) { return d.image; })
            .attr("x", -50)
            .attr("y", -50)
            .attr("width", 100)
            .attr("height", 100);

        // 节点标签
        node.append("text")
            .attr("x", 12)
            .attr("y", 3)
            .text(function(d) { return d.state_str; });

        // 更新图的位置
        simulation.on("tick", function() {
            link
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node
                .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        });
    </script>
</body>
</html>
'''

# 生成HTML文件
html_content = html_template.format(data=json.dumps(utg, indent=4))

with open('graph_visualization.html', 'w') as file:
    file.write(html_content)

print("HTML文件已生成：graph_visualization.html")
