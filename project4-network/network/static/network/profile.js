document.addEventListener('DOMContentLoaded', function() {
    toggleFollow = document.querySelector('#toggle-follow')

    if (toggleFollow !== null) {
        toggleFollow.onclick = () => {
            fetch(`/toggle_follow/${toggleFollow.dataset.username}/`, {
                method: 'PUT'
            })
            .then((response) => {
                if (response.status === 204) {
                    if (toggleFollow.innerText === 'Follow') {
                        toggleFollow.innerText = 'Unfollow';
                    } else {
                        toggleFollow.innerText = 'Follow';
                    }
                }
            });
        }
    }
    loadPosts(document.querySelector('#username').dataset.username);
})   