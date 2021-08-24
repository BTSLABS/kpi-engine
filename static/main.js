
    const rows = document.querySelectorAll("tr[data-href]");
    var rowHtml = "";

    rows.forEach( row =>{
        $.get(`http://10.20.101.180:5000/${row.dataset.host}/health`, function(resp){
            if(resp == "1"){
                $(row).find('.deviceHealth').html(`<i class="fas fa-exclamation-circle red"></i> Update Required`)
            }else if(resp == "0"){
                $(row).find('.deviceHealth').html(`<i class="fas fa-arrow-circle-up green"></i> OK`)
            }
        })
        // if(row.dataset.host == "BTS_TEST_2"){
        //     $(row).find('.deviceHealth').html(`<i class="fas fa-exclamation-circle red"></i> Update Required`)
        // }else{
        //     $(row).find('.deviceHealth').html(`<i class="fas fa-arrow-circle-up green"></i> OK`)
        // }
        row.addEventListener("click", () =>{
            window.location.href = row.dataset.href;
        });
    });


function myFunction(name){
    const host_id = name;

    $(".modal-body #kpiId").val(host_id);

}




