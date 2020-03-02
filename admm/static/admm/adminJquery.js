$(document).ready(function () {



    //for advList.html where advertisements are listed
    $('.owned,.verified').click(function(){
                $(this).css('background-color','lightgray');
                $('.others,.unverified').css('background-color','white');
                $('#id_isowned').val(1);
                $('#submitClick').click();

            });
            $('.others,.unverified').click(function(){
                $('#id_isowned').val(0);
                $(this).css('background-color','lightgray');
                $('.owned,.verified').css('background-color','white');
                $('#submitClick').click();
            });
            $('#closePackPopUp').click(function(){
                $('#packCreate').hide();
            });
            $('#packBtn').click(function(){
                $('#id_isPack').val(1);
                $('#packCreate').toggle();
                $('#offerHeading').hide();
                $('#packHeading').show();
                $('#id_selectedAdvCnt').val($('input:checkbox:checked').length);
            });
            $('#offrBtn').click(function(){
                $('#id_isPack').val(0);
                $('#packCreate').toggle();
                $('#packHeading').hide();
                $('#offerHeading').show();
                $('#id_selectedAdvCnt').val($('input:checkbox:checked').length);
            });
            $('#showChckBoxes').click(function(){
                $('input:checkbox').toggle();
            });

            <!--$('#submitClick').click(function(){-->
                <!--$.ajax({-->
                    <!--type:'POST',-->
                    <!--url:'/adminsite/listadv/',-->
                    <!--data:{-->
                        <!--isowned:$('#id_isowned').val(),-->
                    <!--},-->
                    <!--success:function(){-->
                        <!--alert('done');-->
                    <!--}-->
                <!--});-->
            <!--});-->



  });