import { html } from 'https://unpkg.com/htm/preact/index.mjs?module'
import { useState } from 'https://unpkg.com/preact/hooks/dist/hooks.mjs?module'


export function TabsView (props) {
  const tabIds = props.children.map(child => child.props.id)
  const tabNames = props.children.map(child => child.props.name)

  const initialIndex = (() => {
    let initialIndex = tabIds.indexOf(props.tab)
    return initialIndex === -1 ? 0 : initialIndex
  })()


  const [selectionIndex, setSelectionIndex] = useState(initialIndex)
  const select = tabIndex => {
    window.location.hash = tabIds[tabIndex]
    setSelectionIndex(tabIndex)
  }

  return html`
    <div class="tabs-view">
      <div class="tabs-view-tabs">
        ${tabNames.map((tabName, tabIndex) =>
          tabIndex == selectionIndex
            ? html`<div class="tabs-view-tab selected">
                ${tabName}
              </div>`
            : html`<div class="tabs-view-tab" onclick=${() => select(tabIndex)}>
                ${tabName}
              </div>`
        )}
      </div>
      <div class="tabs-view-output">
        ${props.children[selectionIndex]}
      </div>
    </div>
  `
}
