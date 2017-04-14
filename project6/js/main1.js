 /*Set global variables*/
    "use strict";
    var margin = 75;
    var width = 1150;
    var height =500;
    var fontsize = "12px";
    var titlefont = "20px";
    /*set up draw function for the top_five_delay list*/

    function draw1(data){
        
        /*D3.js setup code */

        var svg = d3.select("body")
        .append("svg").attr("width", width).attr("height", height)
        .append('g').attr('class','chart1')
        

        /*Dimple.js setup code*/

        var myChart = new dimple.chart(svg, data); 
        myChart.defaultColors = [new dimple.color("#06303e")];
        var x = myChart.addCategoryAxis("x", "carrier_name");
        x.title = 'Carrier Name';
        x.fontSize = fontsize;

        var y = myChart.addMeasureAxis("y", "ave_delayed");
        y.title = 'Percentage of Delayed Flights over Totals'
        y.fontSize = fontsize;
        y.tickFormat = '%';
        var series = myChart.addSeries(null, dimple.plot.bar);
        // Handle the hover event - overriding the default behaviour
        series.addEventHandler("mouseover", onHover);
        // Handle the leave event - overriding the default behaviour
        series.addEventHandler("mouseleave", onLeave);

        //Define popup variable//
        var popup; 

        // Event to handle mouse enter
        function onHover(e) {

            // Get the properties of the selected shape
            var cx = parseFloat(e.selectedShape.attr("x"));
            var cy = parseFloat(e.selectedShape.attr("y"));

            // Set the size and position of the popup
            var width = 100; 
            var height = 70;
            
            var x = (cx + width + 10 < svg.attr("width") ?
                cx + 10:
                cx - width-20);

            var y = (cy - height/2 < 0 ?
                15 :
                cy - height/2);
            
            // Create a group for the popup objects
            popup = svg.append('g')
            
            // Add a rectangle surrounding the text
            popup.append('rect')
            .attr("x", x+75)
            .attr("y", y-5)
            .attr("width", width)
            .attr("height", height)
            .attr("rx", 5)
            .attr("ry", 5)
            .style("fill", "#6d6b6b")

            // Add multiple lines of text
            popup.append("text")
            .append("tspan")
            .attr("x", x+85)
            .attr("y", y+20)
            .text("Total Delayed")
            .style("font-size", "14px")

            popup.append("text")
            .append("tspan")
            .attr("x", x+85)
            .attr("y", y+45)
            .text("Flight:" + Math.floor(e.yValue*100)+"%")
            .style("font-size", "14px")
            
            //Add color change for mouseover effect
            d3.select(e.selectedShape[0][0])
            .style("stroke-width", "5px")
            .style("fill", "#18447f")
            .style("stroke", '#211f1f')
        }

        // Event to handle mouse exit
        function onLeave(e) {
            if (popup != null) {
                popup.remove();
            }
            d3.select(e.selectedShape[0][0])
            .style("stroke-width", "0px")  
            .style("stroke", '#211f1f')
            .style("fill", "#06303e")  
        }

        //Set up bar gap for the bar chart
        series.barGap = 0.5;
        myChart.draw();    

        svg.append("text")
        .attr("x", (width / 2))             
        .attr("y", margin/2)
        .attr("text-anchor", "middle")  
        .style("font-size", titlefont) 
        .style("text-decoration", "bold")  
        .text("Top Five Worst Performing Airlines: Envoy and Northwest Airlines are Top the List with 28% in Delayed Flights");
    }

    d3.csv("data/top_five_delay.csv", draw1)