

        function ejecutarAJAX(){

            var xmlhttp;

            var resultado = document.getElementById("my_info_table");

            if(window.XMLHttpRequest){
                xmlhttp = new XMLHttpRequest;
            }else{
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
            }

            var a = document.getElementById("count").value;

            xmlhttp.onreadystatechange = function(){
                if(xmlhttp.readyState == 4 && xmlhttp.status == 200){
                    var mensaje = xmlhttp.responseText;
                    resultado.innerHTML = mensaje;
                    document.getElementById("count").value = parseInt(document.getElementById("count").value)+20;
                    if (document.getElementById("count").value == "200"){
                        document.getElementById("ajax_button").hidden = true
                    }
                }
            }

            xmlhttp.open("GET","/tft/top/"+a,true);
            xmlhttp.send();
        }

function ejecutarAJAX3(amount){
            console.log(amount)
            var xmlhttp;
            var resultado=document.getElementById('streamsBox');
            if(window.XMLHttpRequest){
                xmlhttp = new XMLHttpRequest;
            }else{
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
            }
            xmlhttp.onreadystatechange = function(){
                if(xmlhttp.readyState == 4 && xmlhttp.status == 200){
                    var mensaje = xmlhttp.responseText;
                    resultado.innerHTML = mensaje;
                }
            }
            xmlhttp.open("GET","/tft/"+amount,true);
            xmlhttp.send();
            }

function ejecutarAJAX2(name){
            setTimeout(() => {   
            console.log(name)
            var xmlhttp;

            var resultado = document.getElementById(name);

            if(window.XMLHttpRequest){
                xmlhttp = new XMLHttpRequest;
            }else{
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
            }

            xmlhttp.onreadystatechange = function(){
                if(xmlhttp.readyState == 4 && xmlhttp.status == 200){
                    var mensaje = xmlhttp.responseText;
                    resultado.innerHTML = mensaje;
                }
            }
            xmlhttp.open("GET","/tft/traits/"+name,true);
            xmlhttp.send();
            }, 500);
        }

function ejecutarAJAX4(user_name){

            var xmlhttp;

            var resultado = document.getElementById("my_user_table");

            if(window.XMLHttpRequest){
                xmlhttp = new XMLHttpRequest;
            }else{
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
            }


            xmlhttp.onreadystatechange = function(){
                if(xmlhttp.readyState == 4 && xmlhttp.status == 200){
                    var mensaje = xmlhttp.responseText;
                    resultado.innerHTML = mensaje;
                    document.getElementById("ajax_button").hidden = true
                }
            }

            xmlhttp.open("GET","/tft/user/"+user_name+"/asinc",true);
            xmlhttp.send();
        }