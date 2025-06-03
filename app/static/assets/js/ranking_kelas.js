document.addEventListener('DOMContentLoaded', function() {
    // Load classes for dropdown
    loadClasses();
    loadSemesters();

    // Set up event listeners
    document.getElementById('classSelect6').addEventListener('change', handleSelectionChange);
    document.getElementById('semesterSelect6').addEventListener('change', handleSelectionChange);
});

function loadClasses() {
    fetch('/api/v1/classes')
        .then(response => response.json())
        .then(data => {
            const selectElement = document.getElementById('classSelect6');
            data.forEach(kelas => {
                const option = document.createElement('option');
                option.value = kelas.id;
                option.textContent = kelas.nama;
                selectElement.appendChild(option);
            });
            // Trigger change to load data if there are classes
            if (data.length > 0) {
                handleSelectionChange();
            }
        })
        .catch(error => console.error('Error loading classes:', error));
}

function loadSemesters() {
    fetch('/api/v1/semesterall')
        .then(response => response.json())
        .then(data => {
            const selectElement = document.getElementById('semesterSelect6');
            data.forEach(semester => {
                const option = document.createElement('option');
                option.value = semester.id;
                option.textContent = `${semester.tahun_ajaran} - ${semester.semester}`;
                selectElement.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading semesters:', error));
}

function handleSelectionChange() {
    const classId = document.getElementById('classSelect6').value;
    const semesterId = document.getElementById('semesterSelect6').value;
    
    if (classId && semesterId) {
        fetchRankingData(classId, semesterId);
    }
}

function fetchRankingData(classId, semesterId) {
    // Show loading indicator
    document.getElementById('rankingChart').innerHTML = '<div class="text-center my-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading data...</p></div>';
    
    fetch(`/api/ranking_per_class/${classId}/${semesterId}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                document.getElementById('rankingChart').innerHTML = '<div class="alert alert-info text-center my-5">No ranking data available for the selected class and semester.</div>';
                return;
            }
            
            // Sort data by average score (descending)
            data.sort((a, b) => b.avg_nilai - a.avg_nilai);
            
            // Prepare data for chart
            const studentNames = data.map(item => item.nama);
            const averageScores = data.map((item, index) => {
                // Define colors for medal positions
                let color;
                if (index === 0) color = '#FFD700'; // Gold
                else if (index === 1) color = '#C0C0C0'; // Silver
                else if (index === 2) color = '#CD7F32'; // Bronze
                else color = '#4361ee'; // Default blue
                
                return {
                    y: item.avg_nilai,
                    color: color,
                    rank: index + 1
                };
            });
            
            // Calculate class average
            const classAverage = data.reduce((sum, item) => sum + item.avg_nilai, 0) / data.length;
            
            // Create the chart
            Highcharts.chart('rankingChart', {
                chart: {
                    type: 'column',
                    height: 500
                },
                title: {
                    text: 'Ranking Siswa per Kelas',
                    style: {
                        fontWeight: 'bold'
                    }
                },
                subtitle: {
                    text: `Rata-rata kelas: ${classAverage.toFixed(2)}`
                },
                xAxis: {
                    categories: studentNames,
                    labels: {
                        rotation: -45,
                        style: {
                            fontSize: '11px'
                        }
                    },
                    title: {
                        text: 'Siswa'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Rata-rata Nilai'
                    },
                    plotLines: [{
                        color: '#FF0000',
                        width: 2,
                        value: classAverage,
                        zIndex: 5,
                        dashStyle: 'shortdash',
                        label: {
                            text: 'Rata-rata Kelas',
                            align: 'right',
                            style: {
                                color: '#FF0000',
                                fontWeight: 'bold'
                            }
                        }
                    }]
                },
                legend: {
                    enabled: false
                },
                tooltip: {
                    formatter: function() {
                        return `<b>Rank #${this.point.rank}:</b> ${this.x}<br/>` +
                               `<b>Nilai:</b> ${this.y.toFixed(2)}`;
                    }
                },
                plotOptions: {
                    column: {
                        borderRadius: 5,
                        dataLabels: {
                            enabled: true,
                            formatter: function() {
                                return `#${this.point.rank}`;
                            },
                            style: {
                                fontWeight: 'bold',
                                color: '#FFFFFF',
                                textOutline: '1px contrast'
                            }
                        }
                    }
                },
                series: [{
                    name: 'Rata-rata Nilai',
                    data: averageScores,
                    colorByPoint: true
                }],
                credits: {
                    enabled: false
                }
            });
        })
        .catch(error => {
            console.error('Error loading ranking data:', error);
            document.getElementById('rankingChart').innerHTML = '<div class="alert alert-danger text-center my-5">Error loading data. Please try again later.</div>';
        });
}