$(document).ready(function() {
    // Fetch class data
    $.getJSON('/api/v1/classes', function(data) {
        const classSelect = $('#classSelect');
        data.forEach(kelas => {
            classSelect.append(new Option(kelas.nama, kelas.id));
        });

        // Load semesters for first class
        if (data.length > 0) {
            fetchSemesters(data[0].id);
        }
    });

    // Handle class selection change
    $('#classSelect').on('change', function() {
        const selectedClassId = $(this).val();
        fetchSemesters(selectedClassId);
    });

    // Fetch semester data
    function fetchSemesters(classId) {
        $.getJSON('/api/v1/semesterall', function(data) {
            const semesterSelect = $('#semesterSelect');
            semesterSelect.empty();
            semesterSelect.append(new Option('--Pilih Semester--', ''));
            
            data.forEach(semester => {
                const semesterText = `${semester.tahun_ajaran} - ${semester.semester}`;
                semesterSelect.append(new Option(semesterText, semester.id));
            });
            
            // Enable the semester dropdown
            semesterSelect.prop('disabled', false);
        });
    }

    // Handle semester selection change
    $('#semesterSelect').on('change', function() {
        const selectedClassId = $('#classSelect').val();
        const selectedSemesterId = $(this).val();
        if (selectedClassId && selectedSemesterId) {
            fetchTopPerformers(selectedClassId, selectedSemesterId);
        }
    });

    function fetchTopPerformers(classId, semesterId) {
        // Show loading state
        $('#topPerformersRadarChart').html('<div class="d-flex justify-content-center align-items-center" style="height:400px"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
        
        $.getJSON(`/api/top_performers/${classId}/${semesterId}`, function(data) {
            if (!data.subjects || data.subjects.length === 0) {
                $('#topPerformersRadarChart').html('<div class="alert alert-info text-center my-5">Tidak ada data performa untuk kelas dan semester yang dipilih.</div>');
                return;
            }

            const subjects = data.subjects;
            const students = data.students;
            
            // Prepare data for grouped bar chart
            const categories = subjects;
            const seriesData = [];
            
            // Color palette for students
            const colors = [
                '#4361ee', // Primary blue
                '#3f37c9', 
                '#4895ef',
                '#4cc9f0',
                '#560bad'  // Purple
            ];
            
            // Create series for each student
            students.forEach((student, index) => {
                seriesData.push({
                    name: student.name,
                    data: student.scores,
                    color: colors[index % colors.length]
                });
            });
            
            // Create the chart
            Highcharts.chart('topPerformersRadarChart', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Top Performers by Subject',
                    style: {
                        fontWeight: 'bold'
                    }
                },
                subtitle: {
                    text: 'Comparison of top 5 students across subjects'
                },
                xAxis: {
                    categories: categories,
                    crosshair: true,
                    labels: {
                        rotation: -45,
                        style: {
                            fontSize: '12px'
                        }
                    },
                    title: {
                        text: 'Mata Pelajaran'
                    }
                },
                yAxis: {
                    min: 0,
                    max: 100,
                    title: {
                        text: 'Nilai'
                    },
                    plotLines: [{
                        color: '#FF0000',
                        width: 2,
                        value: 75, // KKM line
                        zIndex: 5,
                        dashStyle: 'shortdash',
                        label: {
                            text: 'KKM',
                            align: 'right',
                            style: {
                                color: '#FF0000',
                                fontWeight: 'bold'
                            }
                        }
                    }]
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                        '<td style="padding:0"><b>{point.y:.1f}</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0,
                        borderRadius: 5,
                        groupPadding: 0.1
                    },
                    series: {
                        dataLabels: {
                            enabled: false,
                            format: '{y:.1f}'
                        }
                    }
                },
                series: seriesData,
                legend: {
                    align: 'center',
                    verticalAlign: 'bottom',
                    layout: 'horizontal',
                    itemStyle: {
                        fontWeight: 'normal'
                    }
                },
                credits: {
                    enabled: false
                },
                responsive: {
                    rules: [{
                        condition: {
                            maxWidth: 500
                        },
                        chartOptions: {
                            legend: {
                                layout: 'horizontal',
                                align: 'center',
                                verticalAlign: 'bottom'
                            }
                        }
                    }]
                }
            });
        }).fail(function() {
            $('#topPerformersRadarChart').html('<div class="alert alert-danger text-center my-5">Gagal memuat data. Silakan coba lagi nanti.</div>');
        });
    }
});