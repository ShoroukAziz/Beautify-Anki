window.addEventListener('load', function () {
   

    if(this.document.querySelector('.rh-container'))
        this.document.querySelector('.rh-container').classList.add('card')
    if(this.document.querySelector('.streak'))
    this.document.querySelector('.streak').classList.add('card-action')


    if(this.document.querySelector('h1')){
        document.querySelector('h1').innerText = document.querySelector('h1').innerText.split("::").join(" :: ")
    }

 

 });
 