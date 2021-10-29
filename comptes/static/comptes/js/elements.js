// Load Faculty options
$("#id_university").change(function () {
    const url = $("#studentForm").attr("data-faculty-url");  // Récupérer l'Url load_faculty
    const universityId = $(this).val();  // Récupérer l'ID de l'entité 
    console.log(universityId)
    if (universityId == "")
    {
        let html_data_false = '<option value="">----------</option>';
        $("#id_ecole").html(html_data_false);
        $("#id_filiere").html(html_data_false);
        $("#id_option").html(html_data_false);
        console.log("Aucune data envoyée")
    }

    else
    {
        $.ajax({                       // Initialiser la requete AJAX
            url: url,                    // Ajouter l'URL de la requete
            data: {
                'university_id': universityId       // Ajouter l'ID de l'université aux paramètres GET
            },
            success: function (data) { 
                let html_data = '<option value="">-----------</option>';
                data.forEach(function (ecole) {
                    html_data += `<option value="${ecole.id}">${ecole.name}</option>`
                });
                console.log(html_data);
                $("#id_ecole").html(html_data)         
            }
        });
    }
});

//Load Faculty
$("#id_ecole").change(function () {
    const url = $("#studentForm").attr("data-entity-url");  
    const facultyId = $(this).val(); 

    if (facultyId == "")
    {
        let html_data_false = '<option value="">-----------</option>';
        $("#id_filiere").html(html_data_false);
        $("#id_option").html(html_data_false);
    }
    else
    {
        $.ajax({                       
            url: url,                    
            data: {
                'ecole_id': facultyId      
            },
            success: function (data) {   
                let html_data = '<option value="">-----------</option>';
                data.forEach(function (entity) {
                    html_data += `<option value="${entity.id}">${entity.name}</option>`
                });
                console.log(html_data);
                $("#id_filiere").html(html_data);               
            }
        });
    }
});

// Load Options of Entity
$("#id_filiere").change(function () {
    const url = $("#studentForm").attr("data-options-url");  
    const entityId = $(this).val();

    if (entityId == "")
    {
        let html_data_false = '<option value="">-----------</option>';
        $("#id_option").html(html_data_false);
    }
    else
    {
        $.ajax({                       
            url: url,                    
            data: {
                'filiere_id': entityId       
            },
            success: function (data) {
                let html_data = '<option value="">-----------</option>';
                data.forEach(function (option) {
                    html_data += `<option value="${option.id}">${option.name}</option>`
                });
                console.log(html_data);
                $("#id_option").html(html_data);
    
                
            }
        });
    }    
});

