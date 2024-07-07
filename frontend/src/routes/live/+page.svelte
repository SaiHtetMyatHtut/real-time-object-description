<script>
	import { onMount, tick } from 'svelte';
    import { browser } from '$app/environment';

    let videoElement;
    let stream;
    let captureInterval;
    let isCameraActive = false;
    let errorMessage = '';

    onMount(async () => {
        if (browser) {
            await checkCameraPermission();
        }
        return () => {
            stopCamera();
        };
    });

    async function checkCameraPermission() {
        try {
            await navigator.mediaDevices.getUserMedia({ video: true });
            console.log('Camera permission granted');
        } catch (error) {
            console.error('Camera permission denied:', error);
            errorMessage = `Camera permission denied: ${error.message}`;
        }
    }

    async function toggleCamera() {
        if (isCameraActive) {
            stopCamera();
        } else {
            await startCamera();
        }
        isCameraActive = !isCameraActive;
    }

    async function startCamera() {
        if (!browser || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            errorMessage = 'Media devices API not supported';
            console.error(errorMessage);
            return;
        }
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } 
            });
            // Wait for the next tick to ensure the video element is rendered
            await tick();
            if (videoElement) {
                videoElement.srcObject = stream;
                await videoElement.play();
                captureInterval = setInterval(captureFrame, 1000);
                errorMessage = '';
            } else {
                throw new Error('Video element not found');
            }
        } catch (error) {
            errorMessage = `Error accessing camera: ${error.message}`;
            console.error(errorMessage, error);
            isCameraActive = false; // Ensure camera state is correctly updated
        }
    }

	function stopCamera() {
		if (stream) {
			const tracks = stream.getTracks();
			tracks.forEach(track => track.stop());
		}
		if (captureInterval) {
			clearInterval(captureInterval);
			captureInterval = null; // Ensure the interval is cleared and reset
		}
		if (videoElement) {
			videoElement.srcObject = null;
		}
		isCameraActive = false; // Ensure camera state is correctly updated
	}

	async function captureFrame() {
		if (!videoElement || !isCameraActive) return; // Add check for isCameraActive

		const canvas = document.createElement('canvas');
		canvas.width = videoElement.videoWidth;
		canvas.height = videoElement.videoHeight;
		canvas.getContext('2d').drawImage(videoElement, 0, 0);

		const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
		const formData = new FormData();
		formData.append('file', blob, `capture-${Date.now()}.jpg`);

		try {
			const response = await fetch('https://58.91.213.145:50337/save_image', {
				method: 'POST',
				body: formData
			});
			if (!response.ok) {
				throw new Error(`Failed to save image: ${response.status} ${response.statusText}`);
			}
			console.log('Frame captured and saved');
		} catch (error) {
			console.error('Error saving captured frame:', error.message);
			// You might want to update some state variable here to show the error to the user
		}
	}
</script>

<main>
    <h1>Live Camera Feed</h1>
    <button on:click={toggleCamera}>
        {isCameraActive ? 'Stop Camera' : 'Start Camera'}
    </button>
    {#if errorMessage}
        <p class="error">{errorMessage}</p>
    {/if}
    <video bind:this={videoElement} autoplay playsinline class:hidden={!isCameraActive}>
        <track kind="captions" />
    </video>
    {#if !isCameraActive}
        <div class="video-placeholder">Camera is off</div>
    {/if}
</main>

<style>
	video, .video-placeholder {
		width: 100%;
		max-width: 640px;
		height: 480px;
		background-color: #f0f0f0;
		display: flex;
		justify-content: center;
		align-items: center;
		border: 1px solid #ccc;
	}
	button {
		margin-bottom: 10px;
	}
    .hidden {
        display: none;
    }
</style>
