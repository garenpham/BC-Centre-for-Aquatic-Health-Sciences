import { html } from 'https://unpkg.com/htm/preact/index.mjs?module'

export function TabView (props) {
    return html`
        <div class="tab-view" data-name="${props.name}">
            ${props.children}
        </div>
    `
}
