// Philip Braunstein
// Some set up

// CONSTANTS
var color = d3.scale.category20();
var data;
var width = 700;
var height = 700;
var nodeRad = 30;
var HUB_SCALE_FACTOR = 2;
var TRANS_DURATION = 1000;
var PAUSE_DURATION = 3000;

var fdg;
var svg = d3.selectAll("div").select(function() {if (this.id == 'viz') return this;})
            .append("svg")
            .attr("width", width)
            .attr("height", height)
// Add bounding box
 svg.append("rect")
   .attr("x", 0)
   .attr("y", 0)
   .attr("width", width)
   .attr("height", height)
   .style("fill", "white")
   .style("stroke", "black");

// Initializes the visualization
function vizIt() {
    var menu = document.getElementById("menu");
    var selectList = document.createElement("select")
    selectList.id = "options";
    menu.appendChild(selectList);

    // Sort data so that it is alphabetical
    data.sort(function (a, b) {
        var verbA = amerikanize(a.root.toLowerCase());
        var verbB = amerikanize(b.root.toLowerCase());
        return (verbA < verbB) ? -1 : 1;
    });

    // Create menu to select verbs
    var i = 0;
    index = null
    for (i = 0; i < data.length; i++) {
        var option = document.createElement("option")
        option.value = data[i]
        option.text = data[i]['root']
        selectList.appendChild(option)

        if (data[i]['root'].localeCompare('sprechen') == 0) {
            selectList.selectedIndex = i;
        }
    }

    // Every time the list changes, tree needs to be rebuilt
    selectList.onchange = (function() {
        buildFDG(data[selectList.selectedIndex]);
    });

    buildFDG(data[selectList.selectedIndex]);  // Build first tree
}

// Removes umlauts and Esszetts for sorting purposes
function amerikanize(verb) {
    verb = verb.replace("ä", "ae");
    verb = verb.replace("ü", "ue");
    verb = verb.replace("ö", "oe");
    verb = verb.replace("ß", "ss");
    return verb;
}

// Builds the tree. Called everytime a new verb-root is selected
function buildFDG(preTree) {
    if (fdg) {
        svg.selectAll(".node").remove();
        svg.selectAll(".link").remove();
    } 
    fdg = d3.layout.force()
        .gravity(0.05)
        .charge(-1000)
        .size([width, height]);
    nodes = [];
    i = 1;
    // Get length of root
    rootLength = preTree.root.length;

    // Create hub node
    nodes.push({"name":preTree.root, "group":i++, "hub":true,"trans":preTree.trans})

    // Create all of the surrounding nodes
    preTree.childWords.forEach(function(word) {
        nodes.push({"name":word.verb, "group":i++,"hub":false,"trans":word.trans});
    });

    links = [];
    // Create links
    for (i = 1; i < nodes.length; i++){
        var newLink = {"source":0, "target":i, "value":6}
        // Index is one behind, because childWords doesn't
        // include the hub node root
        newLink.separ = preTree.childWords[i - 1].separ;
        links.push(newLink);
    }

    fdg.nodes(nodes).links(links).linkDistance(function(thisLink){
        if (thisLink.separ) {
            return 300;}
        else {
            return 150;
        }
      }).start();

    // draw lines for links
    var link = svg.selectAll(".link")
                  .data(links)
                  .enter().append("line")
                  .attr("class", "link")
                  .style("stroke-dasharray", function(d) {if (d.separ) {return 10} else {return 0}})
                  .style("stroke-width", function(d) { if (d.separ) {return Math.sqrt(d.value);} else {return d.value}});

    //create g elemnts for the nodes
    var node = svg.selectAll(".node")
                  .data(nodes)
                  .enter().append("g")
                  .attr("class", "node")
                  .call(fdg.drag);


    // add circles for the nodes
    node.append("circle")		  
                  .attr("r", function(d){
                    // hubs should be bigger
                    if (d.hub) {
                        return HUB_SCALE_FACTOR * nodeRad;
                    } else {
                        return nodeRad;
                    }
                  })
                  .style("fill", function(d) { return color(d.group); });

    // Draw the text label
    node.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", ".35em")
        .style("fill", "gray")
        .style("stroke", "black")
        .text(function(d) {
            if (d.hub) {
                return d.name;
            } else {
                return d.name.slice(0, -rootLength);
            }
        });

    // Create tooltip
    node.append("title")
        .text(function(d) {return d.name + "\n" + d.trans});

    node.on("click", clickEventHandler)


    fdg.on("tick", function() {
        adjustNodesNLinks(node, link);
    });

}

function clickEventHandler(d) {	
            fdg.start();
            // Transition
            var origText = d3.select(this).select("text").text();
            d3.select(this).select("circle").transition().duration(TRANS_DURATION)
              .attr("r", 2 * d3.select(this).select("circle").attr("r"))
              .style("opacity", 0.3)
              .each("start", function() {d3.select(this).style("pointer-events", "none");});

            // Put in translated text
            d3.select(this).select("text").transition().delay(TRANS_DURATION)
              .text(d.trans);

            // Return text to normal  
            d3.select(this).select("text").transition().delay(PAUSE_DURATION)
              .text(origText);

            // Pause, and then transition back to normal
            d3.select(this).select("circle").transition().delay(PAUSE_DURATION).duration(TRANS_DURATION)
              .attr("r", d3.select(this).select("circle").attr("r"))
              .style("opacity", 1)
              .each("end", function () {d3.select(this).style("pointer-events", "auto")});  	
}

function adjustNodesNLinks (node, link) {
    node.attr("transform", function(d) {return "translate(" + clampX(d, this) + "," + clampY(d, this) + ")"; });
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
}



// node is the data, 
// box is the this context of the g svg
// extracts radius and uses this to position node within x bounds
function clampX(node, box) {
    var rad = d3.select(box)[0][0].childNodes[0].r.animVal.value;
    var newVal;
    if (node.x - rad < 0){
        newVal = rad;
    } else if (node.x + rad  > width) {
        newVal = width - rad;
    } else {
        newVal = node.x;
    }
    node.x = newVal;
    return node.x;
}

// node is the data, 
// box is the this context of the g svg
// extracts radius and uses this to position node within y bounds
function clampY(node, box){
    var rad = d3.select(box)[0][0].childNodes[0].r.animVal.value;
    var newVal;
    if (node.y - rad < 0){
        newVal = rad;
    } else if (node.y + rad > height) {
        newVal = height - rad;
    } else {
        newVal = node.y;
    }
    node.y = newVal;
    return node.y
}

function getRandomPos(isXCoord) {
    if (isXCoord) {
        Math.floor(Math.random() * width);
    } else {  // Is height
        Math.floor(Math.random() * height);
    }
}
