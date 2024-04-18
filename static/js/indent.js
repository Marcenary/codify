document.addEventListener('keydown', event => {

    if('TEXTAREA' !== event.target.tagName)
        return
    
    if(event.code !== 'Tab')
        return
    
    event.preventDefault()
    
    let textarea     = event.target
    let selStart     = textarea.selectionStart
    let selEnd       = textarea.selectionEnd
    let before       = textarea.value.substring( 0, selStart )
    let slection     = textarea.value.substring( selStart, selEnd )
    let after        = textarea.value.substr( selEnd )
    let slection_new = ''
    
    if(event.shiftKey) {
        let
            selectBefore = before.substr( before.lastIndexOf( '\n' ) + 1 ),
            isfix = /^\s/.test( selectBefore )
        if (isfix) {
            let fixed_selStart = selStart - selectBefore.length
            before   = textarea.value.substring( 0, fixed_selStart )
            slection = textarea.value.substring( fixed_selStart, selEnd )
        }
        
        let once = false 
        slection_new = slection.replace( /^(\t|[ ]{2,4})/gm, mm => {
        
            if(isfix && !once) {
                once = true
                selStart -= mm.length
            }
        
            selEnd -= mm.length
            return ''
        })
    } else {
        selStart++
    
        if( slection.trim() ){
            slection_new = slection.replace( /^/gm, ()=>{
                selEnd++
                return '\t'
            })
        } else {
            slection_new = '\t'
            selEnd++
        }
    }
    
    textarea.value = before + slection_new + after
    textarea.setSelectionRange(selStart, selEnd)
});