console.log("Are you supposed to be here?");

function toggle_form(id) {
    document.getElementById('edit_btn'+id).classList.toggle('hidden')
    document.getElementById('edit_form'+id).classList.toggle('hidden')
}