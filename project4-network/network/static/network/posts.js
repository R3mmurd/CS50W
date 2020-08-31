function loadPosts(which, page=1) {
    const postsView = document.querySelector('#posts-view')

    fetch(`/posts/${which}/?page=${page}`)
    .then(response => response.json())
    .then(result => {
        // Print posts
        console.log(result);

        if (result.posts.length > 0) {
            let postList = '';

            result.posts.forEach(post => {
                postList += `<div id="block-${post.id}" class="block">`;
                postList += `<a href="/profiles/${post.author}/"><h5>${post.author}</h5></a>`;
                postList += `<div id="post-container-${post.id}">`;
                if (post.me) {
                    postList += `<a class="edit-post" data-post-id="${post.id}" href="javascript:void(0);"><p>Edit</p></a>`;
                }
                postList += `<p id="post-text-${post.id}">${post.text}</p>`;
                postList += `</div>`;
                postList += `<span class="text-muted">${post.timestamp}</span><br>`;

                if (post.can_toggle_like) {
                    postList += `<a href="javascript:void(0);" class="toggle-like" data-post-id="${post.id}">`;
                }
                if (post.liked) {
                    postList += `<i id="heart-${post.id}" class="fa fa-heart" aria-hidden="true" data-liked="true"></i>`;
                } else {
                    postList += `<i id="heart-${post.id}" class="fa fa-heart-o" aria-hidden="true" data-liked="false"></i>`;
                }
                if (post.can_toggle_like) {
                    postList += '</a>';
                }

                postList += `<span class="text-muted" id="likes-counter-${post.id}">${post.likes}</span><br>`;
                postList += '</div>';
            });

            postList += createPaginator(result.num_pages, result.page_number);

            postsView.innerHTML = postList;

            document.querySelectorAll('.page-link').forEach((link) => {
                link.onclick = () => { loadPosts(which, link.dataset.page); };
            });

            updateLikes();            
            updateEditLinks();

        } else {
            postsView.innerHTML += '<h5>There is no posts.</h5>'
        }
    });
}

function createPaginator(numPages, pageNumber) {
    if (numPages <= 1) {
        return '';
    }

    let paginator = '';

    paginator += '<div class="pagination"><nav aria-label="Page navigation"><ul class="pagination">';

    if (pageNumber == 1) {
        paginator += '<li class="page-item disabled">';
    } else {
        paginator += '<li class="page-item">';
    }

    paginator += `<a id="prev" data-page="${pageNumber - 1}" class="page-link" href="javascript:void(0);">Previous</a></li>`
    
    for (i = 1; i <= numPages; ++i) {
        if (i == pageNumber) {
            paginator += '<li class="page-item active">';
        } else {
            paginator += '<li class="page-item">';
        }
        paginator += `<a id="${i}" data-page="${i}" class="page-link" href="javascript:void(0);">${i}</a></li>`;
    }

    if (pageNumber == numPages) {
        paginator += '<li class="page-item disabled">';
    } else {
        paginator += '<li class="page-item">';
    }
    paginator += `<a id="next" data-page="${pageNumber + 1}" class="page-link" href="javascript:void(0);">Next</a></li>`
    paginator += '</ul></nav></div>'

    return paginator;
}

function updateEditLinks() {
    document.querySelectorAll('.edit-post').forEach((link) => {
        link.onclick = () => { editPost(link.dataset.postId); };
    });
}

function editPost(postId) {
    const container = document.querySelector(`#post-container-${postId}`);
    const content = document.querySelector(`#post-text-${postId}`).innerText;

    let form = '<form id=edit-form>';
    form += '<div class="form-group">';
    form += `<textarea class="form-control" rows="2" id="edit-text" required>${content}</textarea>`;
    form += `</div>`;
    form += '<input type="submit" class="btn btn-sm btn-primary" value="Update">';
    form += `<button id="cancel-edit-${postId}" class="btn btn-sm btn-secondary">Cancel</button>`;
    form += '</form>';

    container.innerHTML = form;

    document.querySelector(`#cancel-edit-${postId}`).onclick = () => {
        restorePost(postId, content, container);
    }

    document.querySelector('#edit-form').onsubmit = () => {
        const newContent = document.querySelector('#edit-text').value;
        fetch(`/posts/${postId}/edit/`, {
            method: 'PUT',
            body: JSON.stringify({
                text: newContent
            })
        })
        .then((response) => {
            if (response.status === 204) {
                restorePost(postId, newContent, container);
            } else {
                restorePost(postId, content, container);
            }
        });
        return false;
    }
}

function restorePost(postId, content, container) {
    let restore = `<a class="edit-post" data-post-id="${postId}" href="javascript:void(0);"><p>Edit</p></a>`;
    restore += `<p id="post-text-${postId}">${content}</p>`;
    container.innerHTML = restore;
    updateEditLinks();
}

function updateLikes() {
    document.querySelectorAll('.toggle-like').forEach((link) => {

        link.onclick = () => {
            const postId = link.dataset.postId;

            fetch(`/posts/${postId}/toggle_like/`, {method: 'PUT'})
            .then((response) => {
                const heart = document.querySelector(`#heart-${postId}`);
                const likeCounter = document.querySelector(`#likes-counter-${postId}`);
                if (response.status === 204) {
                    if (heart.dataset.liked === "true") {
                        heart.dataset.liked = "false";
                        heart.className = "fa fa-heart-o";
                        likeCounter.innerText = parseInt(likeCounter.innerText) - 1;
                    } else {
                        heart.dataset.liked = "true";
                        heart.className = "fa fa-heart";
                        likeCounter.innerText = parseInt(likeCounter.innerText) + 1;
                    }
                }
            });
        }
    });
}