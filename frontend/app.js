async function authedFetch(url) {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "index.html";
        return null;
    }
    const response = await fetch(url, {
        headers: {"Authorization": "Bearer " + token},
    });
    if (response.status === 401 || response.status === 403) {
        localStorage.removeItem("token");
        window.location.href = "index.html";
        return null;
    }
    return response;
}

function dmsToDecimal(dms) {
    return dms.Degrees + dms.Minutes / 60 + dms.Seconds / 3600;
}
