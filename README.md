# MALCILLER.IO
#### Video Demo: <https://www.youtube.com/watch?v=6gS1-2rG4Qc&ab_channel=AiTaughtMeHow>
#### Description: 
My journey began as an entry-level call center agent, and through sheer stubborness and ChatGPT, I transitioned into a professional programmer. The acceleration in learning and applying new concepts was staggering. However, as my proficiency grew, the message cap on GPT-4 for ChatGPT Plus became a bottleneck in my professional development.

- **Personalized Chat Interface**: A user-friendly environment reminiscent of ChatGPT's conversational style.
- **API Key Management**: Securely store and manage your OpenAI API key for custom usage.
- **Account Management**: Easy account creation and deletion, giving you full control over your data.


## Technologies Used
This application is built using a stack that includes:

- **Front-end**: HTML, CSS, JavaScript, Bootstrap for responsive design.
- **Back-end**: Python with Flask for server-side logic, and a Postgresql database.
- **APIs**: Integration with OpenAI's API.


## File Descriptions
### Python Files

#### `app.py`
- **Flask Application Initialization**: Sets up the Flask application and configurations including the secret key and database URI.
- **Database Interaction**: Functions to interact with the PostgreSQL database for various operations such as fetching saved messages, user management, and handling API keys.
- **User Authentication and Management**: Includes routes for user login, registration, updating email, resetting password, and account deletion, with necessary validations and flash messages (never got these to display properly).
- **API Key Management**: Routes for handling the collection and updating of OpenAI API keys.
- **Chat Interface**: The core feature that allows users to send messages and receive responses from GPT-4 using their API key. Implements Markdown processing for chat responses and manages message context.
- **User Feedback Mechanisms**: Includes buttons for marking responses as helpful and selecting responses to be included in future context.
- **Error Handling**: Exception handling for database and API interactions to ensure stability and provide user feedback on errors.

#### `forms.py`
- **Flask-WTForms Integration**: Utilizes Flask-WTForms for form handling and validation.
- **RegistrationForm Class**: Defines the user registration form with username, email, password, confirm password fields, and a submit button. Includes validators for data requirement, length constraints, and email formatting.
- **LoginForm Class**: Sets up the login form with username and password fields, along with a submit button. It incorporates validators for data requirement and length constraints.
- **APIKeyForm Class**: Creates a form for API key submission with a single field for the API key and a submit button. It uses validators to ensure the API key is provided and adheres to specified length constraints.


### HTML FILES

### `layout.html`
- **Base Template**: Serves as the base template for other views.
- **Head Section**: Includes a dynamic block for the title, character set meta tag, viewport meta tag for responsive design, Bootstrap CSS link, and a link to my custom styles CSS file.
- **Body Structure**: Provides a structure for the application with extendable blocks for the navigation bar and main content.
- **Custom Footer**: A footer section with a link to Icons8, which provides icons used in the app.
- **JavaScript Integration**: Includes jQuery and Bootstrap JS for interactive components.
- **Dynamic Chat Interface Handling**: A script to handle the layout adjustments of a chat interface, if present, adjusting heights dynamically based on viewport changes and ensuring proper positioning and scrolling behavior.

### `login.html`
- **Navigation Options**: Offers quick links to the 'Create Account' and 'More Info' pages for user convenience.
- **Welcoming Header**: Features a relatable header, briefly explaining the solution to the GPT-4 usage limit issue.
- **Form Setup with Flask-WTF**: Employs Flask-WTF for efficient form handling, covering username and password fields.
- **Client-Side Validation**: Implements form validation on the client side to enhance user experience.
- **JavaScript Functions for Redirection**: Includes straightforward JavaScript functions for navigation to the registration and info pages without page reloads.

### `key_collection.html`
- **Header and Description**: Displays a prominent header for API key registration and a brief description emphasizing support for GPT-4 API and privacy assurance.
- **API Key Field**: Incorporates a form field for the user to input their OpenAI API key.
- **Submit Button**: Features a button with an icon, for API key submission.

### `register.html`
- **Navigation**: Includes a tab for easy navigation back to the Login page.
- **Form Rendering with Flask-WTF**: Utilizes Flask-WTF to create a user-friendly registration form, ensuring efficient data input for username, email, and password.
- **Validation for User Input**: Implements client-side validation for a better and error-free user experience.
- **JavaScript for Smooth Navigation**: A simple JavaScript function to return to the login page without reloading the page.

### `info.html`
- **Description**: Brief background and description of me and the application.
- **JavaScript**: Button and script to handle returning to login without having to reload the page.

### `index.html`
- **Navigation Tabs**: Implements navigation tabs at the top of the page, allowing users to switch between the 'Account' and 'Chat' sections.
- **Account Information**: The 'Account' tab contains user-specific information, included from a separate `user_info.html` partial.
- **Chat Interface**: The 'Chat' tab integrates a chat interface, included from `chat.html`, enabling user interaction with the chat functionality.
- **Tab Switching Script**: Includes a JavaScript snippet to handle the dynamic switching between tabs. Smooth, no-reload transition and manages the active state of each tab.

### `user_info.html`
- **User Interface Layout**: Uses Bootstrap for responsive design, ensuring compatibility across different devices.
- **Account Management Buttons**: Includes buttons for updating email, password, and API key, each with an intuitive icon. Also features buttons for how-to instructions and account deletion.
- **User Information Display**: Shows the user's username and email in a clear format.
- **Dynamic Forms**: Contains forms for updating email, password, and API key, as well as for account deletion. These forms are hidden and can be displayed via button interaction.
- **How-To Instructions**: Provides a hidden section with guidance on using the chat interface, which becomes visible when interacted with.
- **Sign Out Option**: Offers a sign-out button for secure account exit.
- **JavaScript Functionality**: Employs JavaScript for dynamic display and management of forms, enhancing user interaction and page usability.

### `delete_account_confirmation.html`
- **Confirmation Prompt**: Includes a straightforward prompt asking for user confirmation to proceed with account deletion.
- **Checkbox for Final Confirmation**: Incorporates a form checkbox as a necessary step for users to confirm their intention to delete the account.
- **Submit Button**: Features a 'Confirm Delete' button, styled distinctively with a red color to signify the importance and finality of the action.

### `chat.html`
- **Container Layout**: Uses a Bootstrap container for the chat interface.
- **Saved Messages Section**: Hidden section for storing saved messages, utilized for displaying messages preserved from previous sessions.
- **Chat Messages Display Area**: A dedicated space for displaying chat messages, with a light background for readability.
- **Message Input Group**: Includes a textarea for typing messages and a send button.
- **Loading Spinner**: A hidden loading spinner, displayed while messages are being processed.
- **Scroll to Bottom Button**: A button to quickly scroll to the bottom of the chat, becoming visible when needed.
- **JavaScript for Chat Functionality**: 
    - **sendMessage Function**: Handles sending messages to the server and processing responses.
    - **appendMessage Function**: Dynamically adds messages to the chat display area, including special handling for code blocks.
    - **markResponseAsHelpful Function**: Marks a response as helpful, updating the UI accordingly.
    - **includeResponseInContext Function**: Toggles the inclusion of a response in future contexts.
    - **copyToClipboard Function**: Enables copying text to the clipboard, for code snippets.
    - **Event Listeners**: Sets up listeners for loading saved messages and managing scroll behavior.


### CSS File


### `styles.css`
- **Root Variables**: Defines CSS variables for colors, footer height, and input section height for consistent styling across the application.
- **Global Styles**:
    - **Box Sizing**: Sets `box-sizing` to `border-box` for all elements.
    - **Scrollbar Styling**: Customizes the scrollbar appearance using `--button-color`.
- **Text and Image Styling**:
    - **Headers (h1-h6)**: Sets the color of all header tags using `--header-color`.
    - **Image Inversion**: Applies a filter to invert colors of images for visual consistency.
- **Layout and Background**:
    - **HTML and Body**: Styles the entire document's background, text color, and font, and restricts overflow.
    - **Container and Chat Messages**: Styles the main container and chat messages area, including positioning and overflow behavior.
- **Interactive Elements**:
    - **Buttons**: Styles buttons with rounded edges, consistent coloring, and flex display for centering content.
    - **Input Group**: Positions and styles the input group at the bottom of the screen.
    - **Custom Scroll-to-Bottom Button**: Positions and styles a button for scrolling to the bottom of the chat.
- **Messages and Code Blocks**:
    - **User and Chatbot Messages**: Styles messages from the user and chatbot with distinct background colors and padding.
    - **Code Blocks and Toolbars**: Styles code blocks with a specific background color, text color, and scrollbar.
- **Navigation and Forms**:
    - **Nav Items and Links**: Applies background and text color to navigation items and links.
    - **Form Controls**: Styles form controls with consistent background and text color.
- **Buttons and Icons**:
    - **Various Button Types**: Styles different types of buttons (`btn-warning`, `btn-secondary`, etc.) with consistent coloring and border styles.
    - **Helpful Button and Icons**: Styles the helpful button and various icons used in the application, including hover and active states.
