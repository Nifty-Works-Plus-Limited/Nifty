function uploadImage(imageSignedUrl, imageFile) {
    return fetch(imageSignedUrl, {
        method: 'PUT',
        body: imageFile,
        headers: {
            'Content-Type': 'application/octet-stream',
            'X-Goog-Content-Length-Range': '1,1000000000000',
        }, 
    });
}

function uploadVideo(videoSignedUrl, videoFile) {
    return fetch(videoSignedUrl, {
        method: 'PUT',
        body: videoFile,
        headers: {
            'Content-Type': 'application/octet-stream',
            'X-Goog-Content-Length-Range': '1,1000000000000',
        },
    });
}

document.querySelector('form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const imageFile = document.querySelector('#id_image').files[0];
    const videoFile = document.querySelector('#id_movie').files[0];

    const imageSignedUrl = document.querySelector('#image-signed-url').value;
    const videoSignedUrl = document.querySelector('#video-signed-url').value;
    console.log(imageSignedUrl, videoSignedUrl)

    try {
        const [imageResponse, videoResponse] = await Promise.all([
            uploadImage(imageSignedUrl, imageFile),
            uploadVideo(videoSignedUrl, videoFile),
        ]);
        console.log(imageSignedUrl, videoSignedUrl, imageResponse, videoResponse)
        if (!imageResponse.ok || !videoResponse.ok) {
            throw new Error('Error uploading files');
        }

        document.querySelector('form').submit();
    } catch (error) {
        console.error(error);
        // handle error
    }
});
