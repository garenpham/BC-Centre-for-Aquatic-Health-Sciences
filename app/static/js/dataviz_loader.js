const alert = document.getElementById('dataviz-alert'),
    hideAlertButton = document.getElementById('alert-hide-button'),
    startDate = document.getElementById('start-date'),
    endDate = document.getElementById('end-date'),
    loader = document.getElementById('loader'),
    datavizContainer = document.getElementById('dataviz-container'),
    filtersForm = document.getElementById('filters-form')

startDate.oninput = () => {
    endDate.setAttribute('min', startDate.value)
}

filtersForm.onsubmit = event => {
    event.preventDefault()
    const vizImg1 = document.getElementById('viz1'),
        vizImg2 = document.getElementById('viz2'),
        alertMessage = document.getElementById('alert-message'),
        formData = new FormData(filtersForm)

    loader.hidden = false
    datavizContainer.hidden = true

    fetch('/abund-graph', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        loader.hidden = true
        alert.hidden = true
        if (response.status == 500) {
            alertMessage.innerHTML = 'Failed to visualize data:'
                + ' The server failed to generate a response.'
                + ' Try filtering down the dataset with a more specific query.'
            alert.className = 'alert alert-danger alert-dismissible fade show'
            alert.hidden = false
        } else {
            console.log(response.json())
            response.json().then(data => {
                if (data.message == 'Empty') {
                    alertMessage.innerHTML = 'No data is found matching the filter parameters.'
                    alert.className = 'alert alert-warning alert-dismissible fade show'
                    alert.hidden = false
                } else {
                    vizImg1.setAttribute('src', '../static/img/' + data.viz1 + '?' + new Date().valueOf())
                    vizImg2.setAttribute('src', '../static/img/' + data.viz2 + '?' + new Date().valueOf())
                    vizImg1.style.objectFit = 'contain';
                    vizImg2.style.objectFit = 'contain';
                    datavizContainer.hidden = false
                }
            })
        }
    })
}

hideAlertButton.onclick = () => { alert.hidden = true }
