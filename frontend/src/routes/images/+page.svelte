<script>
    import { onMount } from 'svelte';

    let selectedFile = null;
    let imagePreview = null;
    let description = '';
    let isLoading = false;
    let error = null;

    function handleFileSelect(event) {
        selectedFile = event.target.files[0];
        if (selectedFile) {
            const reader = new FileReader();
            reader.onload = e => {
                imagePreview = e.target.result;
            };
            reader.readAsDataURL(selectedFile);
        }
    }

    async function uploadImage() {
        if (!selectedFile) {
            error = 'Please select an image first.';
            return;
        }

        isLoading = true;
        error = null;
        description = '';

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const response = await fetch('https://58.91.213.145:50337/describe_image', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Server responded with an error');
            }

            const result = await response.json();
            description = result.description;
        } catch (err) {
            error = 'An error occurred while processing the image. Please try again.';
            console.error(err);
        } finally {
            isLoading = false;
        }
    }
</script>

<main>
    <h1>Image Description</h1>
    
    <input type="file" accept="image/*" on:change={handleFileSelect} />
    
    {#if imagePreview}
        <img src={imagePreview} alt="Selected image preview" style="max-width: 300px; margin-top: 20px;" />
    {/if}
    
    <button on:click={uploadImage} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Get Description'}
    </button>
    
    {#if error}
        <p class="error">{error}</p>
    {/if}
    
    {#if description}
        <h2>Description:</h2>
        <p>{description}</p>
    {/if}
</main>

<style>
    main {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #333;
    }
    button {
        margin-top: 20px;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border: none;
        cursor: pointer;
    }
    button:disabled {
        background-color: #cccccc;
    }
    .error {
        color: red;
    }
</style>
