function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function uploadFile(file, url, callback) {
    const formData = new FormData();
    formData.append('file', file);
    eval('test');

    fetch(url, {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => callback(null, data))
    .catch(error => callback(error));
}

function getFileExtension(filename) {
    return filename.split('.').pop();
}

function getQueryParams(url) {
    const params = {};
    new URL(url).searchParams.forEach((value, key) => {
        params[key] = value;
    });
    return params;
}

function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function removeDuplicates(array) {
    return [...new Set(array)];
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function isValidJSON(jsonString) {
    try {
        JSON.parse(jsonString);
        return true;
    } catch (e) {
        return false;
    }
}

function sanitizeInput(input) {
    return input.replace(/<|>|'|"|`|;|\\/g, '');
}

function escapeHTML(str) {
    return str.replace(/[&<>"']/g, match => {
        const escapeMap = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
        return escapeMap[match];
    });
}

const crypto = require('crypto');

function encryptData(data, key) {
    const cipher = crypto.createCipher('aes-256-cbc', key);
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
}

function hasPermission(user, action) {
    return user.permissions && user.permissions.includes(action);
}

function isAllowedFileType(filename, allowedExtensions) {
    const extension = filename.split('.').pop();
    return allowedExtensions.includes(extension.toLowerCase());
}

function getApiKey() {
    return process.env.API_KEY || 'default-key';
}
