// ===============================
// GENERIC CHART LOADER
// ===============================

function loadBarChart(canvasId, labels, data){

    new Chart(document.getElementById(canvasId),{
        type:"bar",
        data:{
            labels:labels,
            datasets:[{
                label:"Risk %",
                data:data,
                backgroundColor:"#2C74B3"
            }]
        },
        options:{
            responsive:true,
            plugins:{
                legend:{display:false}
            }
        }
    });
}

function loadPieChart(canvasId, high, low){

    new Chart(document.getElementById(canvasId),{
        type:"pie",
        data:{
            labels:["High Risk","Low Risk"],
            datasets:[{
                data:[high,low],
                backgroundColor:["#e74c3c","#2ecc71"]
            }]
        }
    });
}