document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate classes
    fetch('/api/classes_absensi')
        .then(response => response.json())
        .then(data => {
            const classSelect = document.getElementById('classSelect17');
            classSelect.innerHTML = ''; // Clear previous options
            data.forEach(kelas => {
                const option = document.createElement('option');
                option.value = kelas.id;
                option.text = kelas.nama;
                classSelect.appendChild(option);
            });

            if (data.length > 0) {
                fetchCumulativeAttendanceData(data[0].id, document.getElementById('semesterSelect11').value);
            }
        });

    // Fetch and populate semesters
    fetch('/api/semesterall')
        .then(response => response.json())
        .then(data => {
            const semesterSelect = document.getElementById('semesterSelect11');
            semesterSelect.innerHTML = ''; // Clear previous options
            data.forEach(semester => {
                const option = document.createElement('option');
                option.value = semester.id;
                option.text = `${semester.tahun_ajaran} - ${semester.semester}`;
                semesterSelect.appendChild(option);
            });

            if (data.length > 0) {
                fetchCumulativeAttendanceData(document.getElementById('classSelect17').value, data[0].id);
            }
        });

    // Event listeners for dropdown changes
    document.getElementById('classSelect17').addEventListener('change', function() {
        const selectedClassId = this.value;
        const selectedSemesterId = document.getElementById('semesterSelect11').value;
        fetchCumulativeAttendanceData(selectedClassId, selectedSemesterId);
    });

    document.getElementById('semesterSelect11').addEventListener('change', function() {
        const selectedClassId = document.getElementById('classSelect17').value;
        const selectedSemesterId = this.value;
        fetchCumulativeAttendanceData(selectedClassId, selectedSemesterId);
    });

    // Fetch and render cumulative attendance data
    function fetchCumulativeAttendanceData(classId, semesterId) {
        fetch(`/api/class_absensi/${classId}/${semesterId}`)
            .then(response => response.json())
            .then(data => {
                const studentNames = data.map(item => item.nama);
                const totalSick = data.map(item => item.total_sakit);
                const totalPermission = data.map(item => item.total_izin);
                const totalUnexcused = data.map(item => item.total_tanpa_keterangan);

                const options = {
                    chart: {
                        type: 'area',
                        height: 400
                    },
                    series: [{
                        name: 'Sakit',
                        data: totalSick
                    }, {
                        name: 'Izin',
                        data: totalPermission
                    }, {
                        name: 'Tanpa Keterangan',
                        data: totalUnexcused
                    }],
                    xaxis: {
                        categories: studentNames
                    },
                    yaxis: {
                        labels: {
                            formatter: function(value) {
                                return value.toFixed(0);
                            }
                        }
                    },
                    dataLabels: {
                        enabled: true,
                        formatter: function(value) {
                            return value.toFixed(0);
                        }
                    }
                };

                // Destroy previous chart instance if it exists
                if (window.chartCumulativeAttendance) {
                    window.chartCumulativeAttendance.destroy();
                }

                // Render new chart instance
                window.chartCumulativeAttendance = new ApexCharts(document.querySelector("#cumulativeAttendanceChart"), options);
                window.chartCumulativeAttendance.render();
            })
            .catch(error => console.error('Error loading cumulative attendance data:', error));
    }
});
