document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate classes
    fetch('/api/classes')
        .then(response => response.json())
        .then(data => {
            const classSelect = document.getElementById('classSelect2');
            data.forEach(kelas => {
                const option = document.createElement('option');
                option.value = kelas.id;
                option.text = kelas.nama;
                classSelect.appendChild(option);
            });
        });

    // Fetch and populate semesters
    fetch('/api/semesterall')
        .then(response => response.json())
        .then(data => {
            const semesterSelect = document.getElementById('semesterSelect2');
            data.forEach(semester => {
                const option = document.createElement('option');
                option.value = semester.id;
                option.text = `${semester.tahun_ajaran} - ${semester.semester}`;
                semesterSelect.appendChild(option);
            });

            // Fetch initial progress data for the first class and semester
            const initialClassId = document.getElementById('classSelect2').value;
            const initialSemesterId = data.length > 0 ? data[0].id : null;
            if (initialClassId && initialSemesterId) {
                fetchProgressData(initialClassId, initialSemesterId);
            }
        });

    // Fetch and render progress data for the selected class and semester
    document.getElementById('classSelect2').addEventListener('change', function() {
        const selectedClassId = this.value;
        const selectedSemesterId = document.getElementById('semesterSelect2').value;
        fetchProgressData(selectedClassId, selectedSemesterId);
    });

    document.getElementById('semesterSelect2').addEventListener('change', function() {
        const selectedClassId = document.getElementById('classSelect2').value;
        const selectedSemesterId = this.value;
        fetchProgressData(selectedClassId, selectedSemesterId);
    });

    function fetchProgressData(classId, semesterId) {
        fetch(`/api/progress_per_class/${classId}/${semesterId}`)
            .then(response => response.json())
            .then(data => {
                const progressBarsContainer = document.querySelector('#progressBars');
                progressBarsContainer.innerHTML = ''; // Clear previous charts
                
                data.forEach((item, index) => {
                    const chartId = `progress${index + 1}`;
                    
                    const chartContainer = document.createElement('div');
                    chartContainer.id = chartId;
                    chartContainer.style.marginBottom = '20px';
                    
                    progressBarsContainer.appendChild(chartContainer);
                    
                    Highcharts.chart(chartId, {
                        chart: {
                            type: 'bar',
                            height: 120
                        },
                        title: {
                            text: `${item.guru} - ${item.mapel}`,
                            align: 'center',
                            margin: 0
                        },
                        subtitle: {
                            text: `Progress: ${Math.round(item.progress)}%`,
                            verticalAlign: "bottom"
                        },
                        credits: false,
                        legend: false,
                        tooltip: false,
                        plotOptions: {
                            bar: {
                                borderWidth: 0,
                                borderRadius: 3
                            }
                        },
                        xAxis: {
                            visible: false
                        },
                        yAxis: {
                            visible: true,
                            min: 0,
                            max: 100,
                            title: {
                                text: null
                            },
                            gridLineWidth: 0,
                            labels: {
                                y: -2
                            }
                        },
                        series: [{
                            name: "Fill",
                            data: [100],
                            color: "gray",
                            grouping: false
                        }, {
                            name: "Percentage",
                            data: [item.progress],
                            color: "orange",
                            dataLabels: {
                                enabled: true,
                                inside: true,
                                align: 'right',
                                format: '{point.y}%',
                                style: {
                                    color: 'white',
                                    textOutline: false
                                }
                            }
                        }]
                    });
                });
            })
            .catch(error => console.error('Error loading progress data:', error));
    }
});