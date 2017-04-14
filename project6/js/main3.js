    /*set up draw function for the most_common_delay_cause list*/
    function draw3(data){
        
        /*D3.js setup code */ 

        var svg = d3.select("body")
        .append("svg").attr("width", width).attr("height", height)
        .append('g').attr('class','chart3')

        /*Dimple.js setup code*/

        //Define chart using dimple
        var myChart = new dimple.chart(svg, data);
        var x = myChart.addCategoryAxis("x", ["carrier_name","variable"]);
        x.title = 'Carrier Name';
        x.fontSize = fontsize;

        var y = myChart.addMeasureAxis("y", "value");
        y.title = 'The averaged number of flights';
        y.fontSize = fontsize;
        y.tickFormat = '%';
        var series = myChart.addSeries("variable", dimple.plot.bar);
        var legend = myChart.addLegend(width*0.65, 60, width*0.25, 60, 'right');
        legend.fontSize = fontsize;
        myChart.draw();

        //Add in title
        svg.append("text")
        .attr("x", (width / 2))             
        .attr("y", margin/2)
        .attr("text-anchor", "middle")  
        .style("font-size", titlefont) 
        .style("text-decoration", "bold")  
        .text("Arrival Delay is the Most Common Cause in Delaying Flights During 2005-2015"); 

    }

    d3.csv("data/most_common_delay_cause.csv", draw3)