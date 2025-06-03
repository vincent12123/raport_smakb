document.getElementById('kelasSelectNilaiAkhir').addEventListener('change', function() {
    document.getElementById('downloadFormNilaiAkhir').submit();
});

document.getElementById('kelasSelectAbsensi').addEventListener('change', function() {
    document.getElementById('downloadFormAbsensi').submit();
});

document.getElementById('kelasSelectKegiatanIndustri').addEventListener('change', function() {
    document.getElementById('downloadFormKegiatanIndustri').submit();
});

document.addEventListener('DOMContentLoaded', function() {
    ['downloadFormNilaiAkhir', 'downloadFormAbsensi', 'downloadFormKegiatanIndustri'].forEach(formId => {
        document.getElementById(formId).addEventListener('submit', function(event) {
            event.preventDefault();
            var formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(result => {
                document.getElementById('result').innerHTML = result;
            });
        });
    });
});