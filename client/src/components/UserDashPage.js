import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import {isEqual} from "lodash";
import * as actions from "../actions";
import {BOX_ORDERING, DEFAULT_BOX_ORDERING} from "../constants";
import BoxList from "./BoxList";
import {Link} from "react-router";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {getBoxes} from "../selectors";

import '../styles/UserDashPage.css';


class UserDashPage extends Component {
  componentDidMount() {
    this.fetchBoxes();
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.location.query, this.props.location.query)) {
      // For a case, when changing page or ordering.
      this.fetchBoxes();
    }
  }

  fetchBoxes = () => {
    this.props.fetchBoxes(
        this.props.myUsername,
        this.props.location.query.page || 1,
        BOX_ORDERING[this.props.location.query.order] || DEFAULT_BOX_ORDERING,
        this.props.location.query.q
    );
  };

  render() {
    return (
        <div>
          <PageHeader>My boxes  ({this.props.totalCount})</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <Link
              className='btn btn-success box-new-button'
              to='/boxes/new/'
          >
            New box
          </Link>
          <BoxList
              router={this.props.router}
              boxes={this.props.boxes}
              totalCount={this.props.totalCount}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    myUsername: state.myUsername,
    ...getBoxes(state, props, state.myUsername),
  }
}

export default connect(mapStateToProps, {
  fetchBoxes: actions.loadBoxes,
})(UserDashPage)
