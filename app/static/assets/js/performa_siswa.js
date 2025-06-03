$(document).ready(function() {
    // Fetch and populate classes
    $.getJSON('/api/classes', function(data) {
        const classSelect = $('#classSelect1');
        data.forEach(kelas => {
            classSelect.append(new Option(kelas.nama, kelas.id));
        });

        // Fetch semesters and students for the first class
        if (data.length > 0) {
            fetchSemesters(data[0].id);
            fetchStudents(data[0].id);

            // Automatically fetch individual performance data for the first class, semester, and student
            const selectedClassId = data[0].id;
            fetchSemesters(data[0].id).then(() => {
                const selectedSemesterId = $('#semesterSelect1').val();
                fetchStudents(selectedClassId).then(() => {
                    const selectedStudentId = $('#studentSelect1').val();
                    if (selectedClassId && selectedSemesterId && selectedStudentId) {
                        fetchIndividualPerformance(selectedClassId, selectedSemesterId, selectedStudentId);
                    }
                });
            });
        }
    });

    // Fetch and populate semesters for the selected class
    $('#classSelect1').on('change', function() {
        const selectedClassId = $(this).val();
        fetchSemesters(selectedClassId);
        fetchStudents(selectedClassId);
    });

    function fetchSemesters(classId) {
        return $.getJSON('/api/semesterall', function(data) {
            const semesterSelect = $('#semesterSelect1');
            semesterSelect.empty();
            data.forEach(semester => {
                semesterSelect.append(new Option(`${semester.tahun_ajaran} - ${semester.semester}`, semester.id));
            });
        });
    }

    function fetchStudents(classId) {
        return $.getJSON(`/api/students_in_class/${classId}`, function(data) {
            const studentSelect = $('#studentSelect1');
            studentSelect.empty();
            data.forEach(student => {
                studentSelect.append(new Option(student.nama, student.id));
            });
        });
    }

    // Fetch and render individual student performance when filters are changed
    $('#classSelect1, #semesterSelect1, #studentSelect1').on('change', function() {
        const selectedClassId = $('#classSelect1').val();
        const selectedSemesterId = $('#semesterSelect1').val();
        const selectedStudentId = $('#studentSelect1').val();
        if (selectedClassId && selectedSemesterId && selectedStudentId) {
            fetchIndividualPerformance(selectedClassId, selectedSemesterId, selectedStudentId);
        }
    });

    function fetchIndividualPerformance(classId, semesterId, studentId) {
        $.getJSON(`/api/student_performance/${classId}/${semesterId}/${studentId}`, function(data) {
            const categories = data.subjects;
            const studentScores = data.scores;
            const classAverage = data.class_average;

            Highcharts.chart('individualPerformanceChart', {
                chart: {
                    zoomType: 'xy'
                },
                title: {
                    text: 'Performa Individu Siswa'
                },
                xAxis: [{
                    categories: categories,
                    crosshair: true
                }],
                yAxis: [{ // Primary yAxis
                    labels: {
                        format: '{value}',
                        style: {
                            color: Highcharts.getOptions().colors[1]
                        }
                    },
                    title: {
                        text: 'Nilai',
                        style: {
                            color: Highcharts.getOptions().colors[1]
                        }
                    }
                }],
                tooltip: {
                    shared: true
                },
                legend: {
                    layout: 'vertical',
                    align: 'left',
                    x: 80,
                    verticalAlign: 'top',
                    y: 55,
                    floating: true,
                    backgroundColor: Highcharts.defaultOptions.legend.backgroundColor || 'rgba(255,255,255,0.25)'
                },
                series: [{
                    name: 'Nilai Siswa',
                    type: 'column',
                    data: studentScores,
                    tooltip: {
                        valueSuffix: ''
                    }
                }, {
                    name: 'Rata-rata Kelas',
                    type: 'spline',
                    data: classAverage,
                    tooltip: {
                        valueSuffix: ''
                    }
                }]
            });
        });
    }
});