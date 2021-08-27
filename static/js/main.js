const rows = document.querySelectorAll("tr[data-href]");
var rowHtml = "";

rows.forEach( row =>{
    $.get(`/${row.dataset.host}/health`, function(resp){
        if(resp == "1"){
            $(row).find('.deviceHealth').html(`<i class="fas fa-exclamation-circle red"></i> Update Required`)
        }else if(resp == "0"){
            $(row).find('.deviceHealth').html(`<i class="fas fa-arrow-circle-up green"></i> OK`)
        }
    })
    row.addEventListener("click", () =>{
        window.location.href = row.dataset.href;
    });
});

function myFunction(name){
    const host_id = name;

    $(".modal-body #kpiId").val(host_id);

}

$(document).on('click', '#logout', function(){
    $(".loader").removeClass("d-none");
    setTimeout(()=>{
        window.location = "/";
    }, 500)
})

$('.password-toggle').click(function (){
    $('#password-toggle').toggleClass('fa-eye fa-eye-slash');

    if( $('#password').attr('type') === 'password'){
        $('#password').attr('type','text');
    } else{
        $('#password').attr('type','password');
    }

})

$(document).ready(function(){
    $(".loader").removeClass("d-none");
    setTimeout(()=>{
        $(".loader").addClass("d-none");
    }, 500)
})