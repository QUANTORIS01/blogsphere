    function toggleReply(id){
    const form = document.getElementById('reply-' + id);
    if (form){
        if (form.style.display === 'none' || form.style.display === ''){
            form.style.display = 'block';
        }else{
            form.style.display = 'none';
        }
    }
}