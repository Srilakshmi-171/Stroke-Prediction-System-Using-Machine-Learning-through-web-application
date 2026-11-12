// ===============================
// ADMIN ANALYTICS DASHBOARD
// ===============================

function loadAdminCharts(riskData){

    const high = riskData.filter(r => r > 60).length;
    const low = riskData.length - high;

    loadBarChart("adminBarChart",
        riskData.map((_,i)=>"Patient "+(i+1)),
        riskData
    );

    loadPieChart("adminPieChart", high, low);
}