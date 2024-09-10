// Configuration
const rowsPerPage = 10;
let currentPage = 1;
let totalPages = 1;

// Fetch and Update Data
async function fetchData() {
    try {
        const response = await fetch('/api/data'); // Endpoint to fetch data as JSON
        const data = await response.json();
        updateTable(data);
        totalPages = Math.ceil(data.length / rowsPerPage);
        updatePaginationInfo();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Update Table with New Data
function updateTable(data) {
    const tbody = document.querySelector('#weather-table tbody');
    tbody.innerHTML = '';

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = data.slice(start, end);

    paginatedData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.id}</td>
            <td>${row.temperature}</td>
            <td>${row.humidity}</td>
            <td>${row.rain}</td>
            <td>${row.source}</td>
            <td>${row.timestamp}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Update Pagination Info
function updatePaginationInfo() {
    document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;
}

// Pagination Controls
document.getElementById('prev-btn').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        fetchData();
    }
});

document.getElementById('next-btn').addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        fetchData();
    }
});

// Initial Fetch and Interval Setup
fetchData();
setInterval(fetchData, 5000); // Fetch new data every 5 seconds
