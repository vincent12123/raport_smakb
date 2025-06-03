document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate classes
    fetch('/api/classes_absensi')
        .then(response => response.json())
        .then(data => {
            const classSelect = document.getElementById('classSelect32');
            data.forEach(kelas => {
                const option = document.createElement('option');
                option.value = kelas.id;
                option.text = kelas.nama;
                classSelect.appendChild(option);
            });

            // Fetch initial students for the first class
            if (data.length > 0) {
                fetchStudents(data[0].id);
            }
        });

    // Fetch and populate students for the selected class
    document.getElementById('classSelect32').addEventListener('change', function() {
        const selectedClassId = this.value;
        fetchStudents(selectedClassId);
    });

    // Fetch and render subject scores for the selected student
    document.getElementById('studentSelect').addEventListener('change', function() {
        const selectedStudentId = this.value;
        fetchStudentSubjectScores(selectedStudentId);
    });

    function fetchStudents(classId) {
        fetch(`/api/students_in_class/${classId}`)
            .then(response => response.json())
            .then(data => {
                const studentSelect = document.getElementById('studentSelect');
                studentSelect.innerHTML = ''; // Clear previous options
                data.forEach(student => {
                    const option = document.createElement('option');
                    option.value = student.id;
                    option.text = student.nama;
                    studentSelect.appendChild(option);
                });

                // Fetch initial subject scores for the first student
                if (data.length > 0) {
                    fetchStudentSubjectScores(data[0].id);
                }
            });
    }

    function fetchStudentSubjectScores(studentId) {
        fetch(`/api/student_subject_scores/${studentId}`)
            .then(response => response.json())
            .then(data => {
                const subjects = [...new Set(data.map(item => item.mapel))];
                const semesters = [...new Set(data.map(item => item.semester))].sort();

                const seriesData = semesters.map(semester => {
                    return {
                        name: `Semester ${semester}`,
                        data: subjects.map(subject => {
                            const record = data.find(item => item.mapel === subject && item.semester === semester);
                            return record ? record.avg_nilai : 0;
                        })
                    };
                });

                Highcharts.chart('studentSubjectScoresChart', {
                    chart: {
                        type: 'bar',
                        height: 400
                    },
                    title: {
                        text: 'Nilai Mapel per Siswa'
                    },
                    xAxis: {
                        categories: subjects,
                        title: {
                            text: null
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Nilai',
                            align: 'high'
                        },
                        labels: {
                            overflow: 'justify'
                        }
                    },
                    tooltip: {
                        valueSuffix: ' poin'
                    },
                    plotOptions: {
                        bar: {
                            dataLabels: {
                                enabled: true
                            }
                        }
                    },
                    series: seriesData
                });
            })
            .catch(error => console.error('Error loading student subject scores:', error));
    }
});