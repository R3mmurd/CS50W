document.addEventListener('DOMContentLoaded', function() {
    form = document.querySelector('#post-form');
    if (form !== null) {
        form.onsubmit = function() {
            sendPost();
            return false;
        }
    }

    loadPosts('all');
})

function sendPost() {
    const text = document.querySelector('#post-text');

    fetch('/posts/', {
        method: 'POST',
        body: JSON.stringify({
            text: text.value
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        text.value = "";
        loadPosts('all');
    })
    .catch(() => {
        console.error('Error')
    });

}
  