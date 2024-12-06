/** @odoo-module **/
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { useRef } from "@odoo/owl";

//patch the class ChatterContainer to added the click function
patch(Chatter.prototype ,{
    setup() {
        super.setup();
        this.video = useRef("video");
        this.stop_camera = useRef("stop-camera-button");
        this.canvas = useRef("canvas");
    },
    onClickCamera: function() {
        var self = this;
        var myModal = document.getElementById("myModal");
        myModal.style.display = "block";
    
        // Konfigurasi opsi kamera
        let constraints = {
            audio: false,
            video: {
                facingMode: { ideal: "environment" } // Preferensi kamera belakang
            }
        };
    
        // Akses perangkat media
        navigator.mediaDevices
            .getUserMedia(constraints)
            .then(function(vidStream) {
                var video = self.video.el;
    
                // Set sumber video ke elemen video
                if ("srcObject" in video) {
                    video.srcObject = vidStream;
                } else {
                    video.src = window.URL.createObjectURL(vidStream); // Browser lama
                }
    
                // Play video saat metadata sudah dimuat
                video.onloadedmetadata = function() {
                    video.play();
                };
    
                // Hentikan kamera saat tombol "Cancel" ditekan
                var stopButton = self.stop_camera.el;
                stopButton.addEventListener('click', function() {
                    vidStream.getTracks().forEach(function(track) {
                        track.stop(); // Stop semua track
                    });
    
                    myModal.style.display = "none"; // Sembunyikan modal
                });
            })
            .catch(function(e) {
                console.error("Error accessing media devices:", e.message);
                alert("Tidak dapat mengakses kamera: " + e.message);
            });
    },    
    /**
    Capture the image
    **/
    ImageCapture: function() {
        let canvas = this.canvas.el;
        let video = this.video.el;
    
        // Set canvas size to match the video resolution
        canvas.width = video.videoWidth; // Resolusi asli video
        canvas.height = video.videoHeight;
    
        // Capture frame from the video to the canvas
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    
        // Convert canvas content to an image with higher quality
        let image_data_url = canvas.toDataURL('image/jpeg', 0.9); // Kualitas 90%
    
        // Convert base64 to a file object
        let [header, base64Data] = image_data_url.split(',');
        let mime = header.match(/:(.*?);/)[1];
        let binary = atob(base64Data);
        let u8arr = new Uint8Array(binary.length);
    
        for (let i = 0; i < binary.length; i++) {
            u8arr[i] = binary.charCodeAt(i);
        }
    
        let file = new File([u8arr], 'image.jpeg', { type: mime });
    
        // Upload the file
        this.attachmentUploader.uploadFile(file);
    
        // Hide the modal
        myModal.style.display = "none";
        
    },    
});
