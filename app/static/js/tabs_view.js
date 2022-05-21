import { html } from 'https://unpkg.com/htm/preact/index.mjs?module'
import { useState, useEffect } from 'https://unpkg.com/preact/hooks/dist/hooks.mjs?module'


export function TabsView (props) {
  const tabIds = props.children.map(child => child.props.id)
  const tabNames = props.children.map(child => child.props.name)

  const [selectionIndex, setSelectionIndex] = useState(0)
  const select = tabIndex => {
    window.location.hash = tabIds[tabIndex]
    setSelectionIndex(tabIndex)
  }

  useEffect(() => {
    const tabIndex = Math.max(0, tabIds.indexOf(props.tab))
    setSelectionIndex(tabIndex)
  }, [props.tab])

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
