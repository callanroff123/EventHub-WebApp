document.addEventListener("DOMContentLoaded", () => {

    // Edit form will appear when the user clicka the 'Edit' button
    // In particular, the edit post form (class="edit-form") will have its syle changed to display=block
    document.querySelectorAll(".edit-link").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const postId = link.getAttribute("data-post-id");
            document.getElementById(`post-body-${postId}`).style.display = 'none';
            document.getElementById(`edit-form-${postId}`).style.display = "block";
        });
    });

    document.querySelectorAll(".hide-link").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const postId = link.getAttribute("data-post-id");
            document.querySelector(`.post-top-original-${postId}`).style.display = 'none';
            document.querySelector(`.post-top-${postId}`).style.display = 'block';
        });
    });

    document.querySelectorAll(".unhide-link").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const postId = link.getAttribute("data-post-id");
            document.querySelector(`.post-top-original-${postId}`).style.display = 'block';
            document.querySelector(`.post-top-${postId}`).style.display = 'none';
        });
    });

    // Opposite to the above. When the user clicks cancel on the post edit form, the form will hide and the original post will reappear
    document.querySelectorAll(".cancel-edit").forEach(button => {
        button.addEventListener("click", () => {
            const postId = button.getAttribute("data-post-id");
            document.getElementById(`edit-form-${postId}`).style.display = "none";
            document.getElementById(`post-body-${postId}`).style.display = "block"
        })
    });

    // Save the edited post to the database (under the orignal post ID) 
    document.querySelectorAll(".save-edit").forEach(button => {
        button.addEventListener("click", () => {
            const postId = button.getAttribute("data-post-id");
            const body = document.getElementById(`edit-body-${postId}`).value;
            fetch(`/edit_post/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("input[name=csrf_token]").value
                },
                body: JSON.stringify({ post_body: body })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`post-body-${postId}`).textContent = data.updated_body;  
                } else {
                    alert("Error - Cannot update post :/");
                }
                document.getElementById(`edit-form-${postId}`).style.display = "none";
                document.getElementById(`post-body-${postId}`).style.display = "block";
            })
            .catch(error => console.error({"Error": error}))
        });
    });

    document.querySelectorAll(".delete-link").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const postId = link.getAttribute("data-post-id");
            document.querySelector(`.post-top-original-${postId}`).style.display = 'none';
            document.querySelector(`.post-top-delete-${postId}`).style.display = 'block';
            fetch(`/delete_post/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("input[name=csrf_token]").value
                },
                body: JSON.stringify({ post_id: postId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Post successfuly deleted"); 
                } else {
                    alert("Error - Cannot update post :/");
                }
            })
            .catch(error => console.error({"Error": error}))
        });
    });

});