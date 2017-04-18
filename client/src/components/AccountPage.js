import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader, Tab, Tabs} from "react-bootstrap";
import MyBreadcrumbs from "./MyBreadcrumbs";
import AccountBasicForm from "./AccountBasicForm";
import AccountPasswordsForm from "./AccountPasswordsForm";


class AccountPage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
    }
  }

  render() {
    return (
        <div>
          <PageHeader>Account settings</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <Tabs id="account-tabs">
            <Tab eventKey={1} title="Basic">
              <AccountBasicForm user={this.props.user} />
            </Tab>
            <Tab eventKey={2} title="Change password">
              <AccountPasswordsForm username={this.props.myUsername}/>
            </Tab>
          </Tabs>
        </div>
    );
  }
}

function mapStateToProps(state) {
  const myUsername = state.myUsername;
  const user = state.entities.users[state.myUsername];
  return {
    myUsername,
    user,
  }
}

export default connect(mapStateToProps, {
})(AccountPage)
