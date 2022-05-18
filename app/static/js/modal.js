import cc from 'https://unpkg.com/classcat?module';
import { html, render, Component } from 'https://unpkg.com/htm/preact/index.mjs?module'
import { useState, useRef, useEffect } from 'https://unpkg.com/preact@10.7.2/hooks/dist/hooks.mjs?module';


export class ModalAction {
  constructor(text, flags, options) {
    this.text = text
    this.flags = flags
    this.disabled = options ? options.disabled : false  // TODO: optional chaining
    this.callback = options && options.callback         // TODO: optional chaining
  }
}

export function Modal(props) {
  const [isShown, setShown] = useState(false)
  const [isOpen, setOpen] = useState(false)
  const [isAnimating, setAnimating] = useState(false)
  const close = () => !isAnimating && setOpen(false)

  // HACK: trigger reflush using props
  if (!isShown && props.shown) {
    setOpen(true)
    setShown(true)
    setAnimating(true)
  }

  const modalWrapRef = useRef(null)
  const modalRef = useRef(null)

  useEffect(() => {
    const modal = modalRef && modalRef.current  // TODO: optional chaining
    if (!modal) {
      return
    }

    modal.addEventListener('animationend', function onEnd() {
      modal.removeEventListener('animationend', onEnd)
      if (modal.classList.contains('anim-enter')) {
        modal.classList.remove('anim-enter')
      } else if (modal.classList.contains('anim-exit')) {
        modal.classList.remove('anim-exit')
        props.shown = false
        setShown(false)
      }
      setAnimating(false)
    })
  }, [isOpen])

  return html`
    <div class=${cc([
        "custom-modal-wrap",
        isShown ? "anim-show" : "anim-hide"
      ])}>
      <div ref=${modalRef} class=${cc([
        "custom-modal",
        isOpen ? "anim-enter" : "anim-exit"
      ])}>
        <h4 class="custom-modal-title">${props.title || 'Untitled modal'}</h4>
        <hr/>

        <form class="needs-validation" method="POST" enctype="multipart/form-data">
          ${props.children}

          <div class="custom-modal-actions">
            ${props.actions && props.actions.map(action => html`
              <button
                type=${action.flags.includes('primary') && !action.callback
                  ? 'submit'
                  : 'button'}
                class=${cc([
                  "custom-modal-action",
                  "btn",
                  `btn-${action.flags.join('-')}`,
                  ...(action.disabled ? ["disabled"] : [])
                ])}
                onClick=${() => {
                  if (action.disabled) {
                    return
                  }
                  action.callback && action.callback()  // TODO: optional chaining
                  close()
                }}
              >${action.text}</button>
            `)}
          </div>
        </form>

        <button class="custom-modal-close" onClick=${close}>
          <i class="bi-x-lg"></i>
        </button>
      </div>
      <div class="custom-modal-overlay" onClick=${close}></div>
    </div>
  `
}
