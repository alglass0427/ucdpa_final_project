const modalStyle = `
  #backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    background: rgba(0, 0, 0, 0.75);
    z-index: 10;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease-out;
  }

  :host([opened]) #backdrop,
  :host([opened]) #modal {
    opacity: 1;
    pointer-events: all;
  }

  :host([opened]) #modal {
    top: 1rem;
  }

  #modal {
    position: fixed;
    top: 1rem;
    left: 50%;
    transform: translateX(-50%);
    width: 1000px;
    max-width: 90%;
    max-height: 80vh; /* Limit the height of the modal */
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
    z-index: 100;
    opacity: 0;
    pointer-events: none;
    transition: all 0.3s ease-out;
    display: flex;
    flex-direction: column;
  }

  header {
    padding: 1rem;
    border-bottom: 1px solid #ccc;
    flex-shrink: 0; /* Prevent header from shrinking */
  }

  #main {
    padding: 1rem;
    flex-grow: 1; /* Allow the main section to take available space */
    overflow-y: auto; /* Enable scrolling if content overflows */
  }

  #actions {
   
    padding: 0.25rem;
    display: flex;
    justify-content: flex-end;
    flex-shrink: 0; /* Prevent actions section from shrinking */
  }

  #actions button {
    margin: 0 0.25rem;
  }


@media (max-width: 1000px) {
  #modal {
    width: 650px;
    height: auto;
    max-width: auto;
    max-height: 95vh;
    padding: 0.25rem;
  }
      #main {
    padding: 0.25rem;
    }
}

@media (max-width: 480px) {
  #modal {
    width: 600px;
    width: 100%;
    padding: 0.25rem;
    max-height: 90vh;
  }

}

`;

class Modal extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.isOpen = false;

    this.shadowRoot.innerHTML = `
    <style>${modalStyle}</style>
    <div id="backdrop"></div>
    <div id="modal">
      <section id="main">
        <slot></slot>
      </section>
      <section id="actions">
        <button id="cancel-btn">Close</button>
      </section>
    </div>
  `

//<button id="confirm-btn">Confirm</button>
    const backdrop = this.shadowRoot.querySelector('#backdrop');
    const cancelButton = this.shadowRoot.querySelector('#cancel-btn');
    // const confirmButton = this.shadowRoot.querySelector('#confirm-btn');
    
    backdrop.addEventListener('click', this._cancel.bind(this));
    cancelButton.addEventListener('click', this._cancel.bind(this));
    // confirmButton.addEventListener('click', this._confirm.bind(this));
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'opened') {
      this.isOpen = this.hasAttribute('opened');
    }
  }

  static get observedAttributes() {
    return ['opened'];
  }

  open() {
    this.setAttribute('opened', '');
  }

  hide() {
    this.removeAttribute('opened');
  }

  _cancel(event) {
    this.hide();
    const cancelEvent = new Event('cancel', { bubbles: true, composed: true });
    this.dispatchEvent(cancelEvent);
  }

  _confirm(event) {
    this.hide();
    const confirmEvent = new Event('confirm', { bubbles: true, composed: true });
    this.dispatchEvent(confirmEvent);
  }
}
customElements.define('uc-modal', Modal);


class Footer extends HTMLElement {




}