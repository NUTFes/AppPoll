
var svg = d3.select('div#main')
            .append("svg")
            .attr({
                width:80%,
                height:80%,
            });
var dataset = [1,2,3,4,5,25]
svg.selectAll("circle")
    .data(dataset)
    .enter()
    .append("circle")
    .attr({
        x: function(d, i){ return i * (w / dataset.length);},
        y: function(d) { return h - (d*4);},
        width:w/dataset.length - 10,
        height: function(d){ return d * 4;}
    })

