import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import {isEqual} from "lodash";
import * as actions from "../actions";
import {BOX_ORDERING, DEFAULT_BOX_ORDERING} from "../constants";
import BoxList from "./BoxList";
import {getBoxes} from "../selectors";


class BoxSearchPage extends Component {
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
        null,
        this.props.location.query.page || 1,
        BOX_ORDERING[this.props.location.query.order] || DEFAULT_BOX_ORDERING,
        this.props.location.query.q
    );
  };

  render() {
    return (
        <div>
          <PageHeader>Search results ({this.props.totalCount})</PageHeader>
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
    ...getBoxes(state, props, '__search__'),
  }
}

export default connect(mapStateToProps, {
  fetchBoxes: actions.loadBoxes,
})(BoxSearchPage)
